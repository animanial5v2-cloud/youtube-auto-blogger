import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import axios from 'axios';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { randomInt } from 'crypto';
import { YoutubeTranscript } from 'youtube-transcript';
import play from 'play-dl';
import { exec } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import multer from 'multer';
import fs from 'fs';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5001;

app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true })); // for form data

// --- 정적 파일 제공 ---
app.use(express.static(__dirname));

// --- Multer 설정 (임시 디렉토리에 파일 저장) ---
const upload = multer({ dest: os.tmpdir() });

// --- [Helper 1] Pexels에서 스톡 이미지 가져오기 (키워드 배열 및 대체 검색 로직 적용) ---
async function fetchImageFromPexels(keywords, apiKey) {
    console.log(`>> Pexels 이미지 검색 요청 수신 (키워드: ${keywords.join(', ')})`);
    if (!apiKey) {
        console.log("[경고] Pexels API 키가 제공되지 않았습니다.");
        return null;
    }
    console.log(`>> Pexels API 키 사용 중: ${apiKey.substring(0, 5)}...${apiKey.substring(apiKey.length - 5)}`);
    if (!keywords || keywords.length === 0) {
        console.log("[경고] 검색할 Pexels 키워드가 없습니다.");
        return null;
    }

    for (const keyword of keywords) {
        const query = keyword.trim();
        if (!query) continue;

        console.log(`>> Pexels에서 '${query}' 키워드로 이미지 검색 시도...`);
        const API_URL = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&per_page=15&orientation=landscape`;
        try {
            const pexelsResponse = await axios.get(API_URL, { headers: { 'Authorization': apiKey } });
            const photos = pexelsResponse.data.photos;
            if (photos && photos.length > 0) {
                const photo = photos[randomInt(photos.length)];
                const imageUrl = photo.src.large2x;
                console.log(`>> Pexels 이미지 다운로드 중: ${imageUrl}`);
                const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
                const imageBuffer = Buffer.from(imageResponse.data, 'binary');
                const base64Image = imageBuffer.toString('base64');
                const mimeType = imageResponse.headers['content-type'] || 'image/jpeg';
                console.log(`>> Pexels 이미지 처리 완료! ('${query}' 키워드 사용)`);
                return `data:${mimeType};base64,${base64Image}`;
            }
            console.warn(`[정보] Pexels에서 '${query}'에 대한 이미지를 찾지 못했습니다. 다음 키워드로 넘어갑니다.`);
        } catch (error) {
            console.error(`[오류] Pexels 처리 중 오류 ('${query}' 키워드): ${error.message}`);
            // 한 키워드 실패 시 다음 키워드로 계속 진행
        }
    }

    console.error(`[실패] 제공된 모든 키워드(${keywords.join(', ')})로 Pexels 이미지를 찾지 못했습니다.`);
    return null;
}


// --- [Helper 2] Google Cloud Imagen 2로 AI 이미지 생성 ---
async function generateAiImage(projectId, topic, accessToken) {
    console.log(">> Imagen 2 이미지 생성 요청 수신...");
    if (!projectId || !accessToken) {
        console.log("[경고] GCP Project ID 또는 Access Token이 없습니다.");
        return null;
    }
    const API_ENDPOINT = `https://us-central1-aiplatform.googleapis.com/v1/projects/${projectId}/locations/us-central1/publishers/google/models/imagegeneration@006:predict`;
    const prompt = `A high-quality, photorealistic, cinematic style image representing the concept of '${topic}', suitable for a professional blog post header.`;
    try {
        const response = await axios.post(
            API_ENDPOINT,
            { instances: [{ prompt: prompt }], parameters: { sampleCount: 1 } },
            { headers: { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json' } }
        );
        const prediction = response.data.predictions[0];
        if (prediction && prediction.bytesBase64Encoded) {
            console.log(">> Imagen 2 이미지 생성 완료!");
            return `data:image/png;base64,${prediction.bytesBase64Encoded}`;
        }
        console.warn("[경고] Imagen 2 API가 이미지 데이터를 반환하지 않았습니다. 이미지 없이 진행합니다.");
        return null;
    } catch (error) {
        console.error(`[오류] Imagen 2 API 호출 중 오류: ${error.response?.data?.error?.message || error.message}`);
        return null;
    }
}

// --- [Helper 3-1] 데이터 URI를 Gemini가 이해하는 Part로 변환 ---
function dataUriToGenerativePart(uri, mimeType) {
    const match = uri.match(/^data:(.+);base64,(.+)$/);
    if (!match) throw new Error('Invalid data URI.');
    const [_, detectedMimeType, data] = match;
    return { inlineData: { mimeType: mimeType || detectedMimeType, data } };
}

// --- [Helper 3-2] Gemini 응답에서 JSON 객체 정리 및 파싱 (강화된 버전) ---
function parseGeminiJsonResponse(rawText) {
    console.log(">> Gemini 응답에서 JSON 추출 시도...");
    
    const jsonStart = rawText.indexOf('{');
    const jsonEnd = rawText.lastIndexOf('}');

    if (jsonStart === -1 || jsonEnd === -1 || jsonEnd < jsonStart) {
        console.error("[치명적 오류] Gemini 응답에서 유효한 JSON 객체({ ... })를 찾지 못했습니다.");
        console.error("수신된 원본 텍스트:", rawText);
        throw new Error("AI 응답에서 JSON 객체를 찾을 수 없습니다.");
    }

    const jsonString = rawText.substring(jsonStart, jsonEnd + 1);

    try {
        const parsed = JSON.parse(jsonString);
        console.log(">> JSON 파싱 성공!");
        return parsed;
    } catch (error) {
        console.error("[치명적 오류] Gemini가 반환한 JSON을 파싱하는 데 실패했습니다.", error);
        console.error("추출된 JSON 문자열:", jsonString);
        console.error("수신된 원본 텍스트:", rawText);
        throw new Error("AI 응답이 유효한 JSON 형식이 아닙니다.");
    }
}

// --- [Helper 3-3] Google Gemini로 텍스트 콘텐츠 생성 (JSON 출력 방식) - 강화된 프롬프트 ---
async function generateTextContent(apiKey, topic, imageUrl, modelName, tone, audience) {
    const effectiveModelName = modelName || "gemini-1.5-pro-latest";
    console.log(`>> Gemini 텍스트 생성 요청 수신 (모델: ${effectiveModelName})...`);
    
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: effectiveModelName });
    const imagePart = imageUrl ? dataUriToGenerativePart(imageUrl) : null;
    
    const basePrompt = `
    당신은 전문 SEO 콘텐츠 작가입니다. 주어진 지침에 따라 블로그 게시물을 생성하고, 반드시 지정된 JSON 형식으로만 응답해야 합니다.

    **주제:** "${topic}"
    **글쓰기 톤 & 스타일:** ${tone || '전문적이고 유익하게'}
    **타겟 독자:** ${audience || '일반 대중'}

    **[매우 중요] 출력 형식:**
    - 당신의 전체 응답은 반드시 아래 구조를 따르는 단일 JSON 객체여야 합니다.
    - JSON 외부에는 어떠한 설명이나 추가 텍스트도 포함해서는 안 됩니다.

    \`\`\`json
    {
      "title": "SEO에 최적화된, 흥미로운 한글 제목",
      "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. 서론, 본론, 결론을 포함해야 합니다.",
      "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요. (예: modern smartphone, user interface, mobile technology)",
      "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용."
    }
    \`\`\`

    **[필수 규칙]**
    1.  **\`content_with_placeholder\` 필드:** 이 필드에 '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다. 이를 누락하면 당신의 응답은 처리될 수 없습니다.
    2.  **HTML 구조:** 본문 내용은 \`<h2>\`, \`<h3>\`, \`<p>\`, \`<ul>\`, \`<li>\` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
    ${imageUrl ? `3. **이미지 문맥:** 제공된 이미지를 분석하여, '[IMAGE_HERE]' 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.` : ''}
    `;
    const requestPayload = [basePrompt];
    if (imagePart) requestPayload.push(imagePart);

    try {
        const result = await model.generateContent(requestPayload);
        const response = await result.response;
        const generatedText = response.text();
        
        console.log(">> Gemini 텍스트 생성 완료!");
        return parseGeminiJsonResponse(generatedText);
    } catch (error) {
        console.error(`[오류] Gemini API 호출 중 오류: ${error.message}`);
        throw new Error(`Gemini API 오류: ${error.message}`);
    }
}

// --- [Helper 4] 생성된 HTML에 이미지 태그 삽입 (SEO alt 태그 적용) ---
function insertImageIntoHtml(content_with_placeholder, imageUrl, seoFilename, fallback_alt_text) {
    if (!imageUrl) {
        return content_with_placeholder.replace(/\[IMAGE_HERE\]/g, ''); // 이미지가 없으면 플레이스홀더 제거
    }

    // 키워드를 사용하여 SEO에 친화적인 alt 텍스트 생성, 없으면 fallback 사용
    let altText = fallback_alt_text;
    if (seoFilename) {
        altText = seoFilename.replace(/-/g, ' '); // 'iphone-vs-galaxy' -> 'iphone vs galaxy'
    }
    
    const safeAltText = altText.replace(/"/g, '&quot;');
    const imageTag = `<img src="${imageUrl}" alt="${safeAltText}" style="width:100%; height:auto; border-radius:8px; margin-top: 1em; margin-bottom: 1em;">`;
    
    if (content_with_placeholder.includes('[IMAGE_HERE]')) {
        return content_with_placeholder.replace('[IMAGE_HERE]', imageTag);
    }
    
    console.warn("[경고] Gemini가 '[IMAGE_HERE]' 플레이스홀더를 생성하지 않았습니다. 이미지를 본문 상단에 추가합니다.");
    // h1 태그가 있다면 그 바로 뒤에, 없다면 맨 앞에 이미지를 추가
    const h1EndIndex = content_with_placeholder.indexOf('</h1>');
    if (h1EndIndex !== -1) {
        return content_with_placeholder.slice(0, h1EndIndex + 5) + imageTag + content_with_placeholder.slice(h1EndIndex + 5);
    }
    
    return imageTag + content_with_placeholder;
}


// --- [Helper 5-1] YouTube 스크립트 추출 및 결합 (오류 처리 강화) ---
async function fetchAndCombineTranscripts(urls) {
    console.log(">> YouTube 스크립트 추출 요청 수신...");
    let combinedTranscript = "";
    let videoCount = 0;
    const preferredLanguages = ['ko', 'en'];

    for (const url of urls) {
        const validation = await play.validate(url);
        if (validation !== 'yt_video') {
            console.error(`[실패] 유효하지 않은 YouTube URL입니다: ${url}`);
            continue;
        }
        
        let transcriptFound = false;
        for (const lang of preferredLanguages) {
            try {
                console.log(`>> URL [${url}]에 대해 '${lang}' 언어 스크립트 추출 시도...`);
                const transcript = await YoutubeTranscript.fetchTranscript(url, { lang });
                if (transcript && transcript.length > 0) {
                    const transcriptText = transcript.map(item => item.text).join(' ');
                    combinedTranscript += `--- Video ${videoCount + 1} (Lang: ${lang}) Transcript ---\n${transcriptText}\n\n`;
                    videoCount++;
                    transcriptFound = true;
                    console.log(`>> '${lang}' 언어 스크립트 추출 성공!`);
                    break; 
                }
            } catch (error) {
                const errorMessage = error.message || '';
                if (errorMessage.includes('Could not find a transcript for the video') || errorMessage.includes('No transcripts are available for this video')) {
                    let availableLangs = '';
                    const match = errorMessage.match(/Available languages: (.*)/);
                    if (match && match[1]) {
                        availableLangs = ` (사용 가능 언어: ${match[1]})`;
                    }
                    console.warn(`[정보] URL [${url}]에서 '${lang}' 언어 자막을 찾을 수 없습니다.${availableLangs}`);
                } else {
                    console.error(`[오류!] URL [${url}]의 '${lang}' 자막 처리 중 예기치 않은 오류 발생. 오류: ${errorMessage}`);
                }
            }
        }

        if (!transcriptFound) {
            console.error(`[실패] URL [${url}]에 대해 지원되는 언어(${preferredLanguages.join(', ')})의 스크립트를 최종적으로 찾지 못했습니다.`);
        }
    }
    
    if (videoCount === 0) {
        return null;
    }
    
    console.log(`>> 총 ${videoCount}개의 영상에서 스크립트를 성공적으로 추출했습니다.`);
    return combinedTranscript;
}

// --- [Helper 5-2] YouTube 오디오 추출 (Base64) ---
async function fetchAudioAsBase64(url) {
    console.log(`>> YouTube 오디오 스트림 다운로드 시작: ${url}`);
    const validation = await play.validate(url);
    if (validation !== 'yt_video') {
        throw new Error("유효하지 않은 YouTube URL입니다.");
    }

    try {
        const streamInfo = await play.stream(url, { quality: 2 });
        const audioStream = streamInfo.stream;
        const chunks = [];

        return new Promise((resolve, reject) => {
            audioStream.on('data', (chunk) => chunks.push(chunk));
            audioStream.on('end', () => {
                console.log('>> 오디오 스트림 다운로드 완료. Base64로 인코딩합니다.');
                const audioBuffer = Buffer.concat(chunks);
                const audioBase64 = audioBuffer.toString('base64');
                const mimeType = streamInfo.type === 'webm' ? 'audio/webm' : 'audio/mpeg';
                resolve({ audioBase64, mimeType });
            });
            audioStream.on('error', (error) => {
                console.error(`[오류] YouTube 오디오 스트림 처리 중 오류: ${error.message}`);
                reject(new Error(`YouTube 오디오 처리 실패: ${error.message}`));
            });
        });
    } catch (error) {
        console.error(`[오류] play-dl 스트림 생성 중 오류: ${error.message}`);
        throw new Error(`play-dl을 사용하여 오디오 스트림을 가져오는 데 실패했습니다: ${error.message}`);
    }
}

// --- [Helper 6-1] YouTube 스크립트 기반 텍스트 생성 (JSON 출력) ---
async function generateTextFromTranscripts(apiKey, transcripts, imageUrl, modelName, tone, audience) {
    const effectiveModelName = modelName || "gemini-1.5-pro-latest";
    console.log(`>> Gemini 텍스트 생성 요청 (YouTube 스크립트 기반, 모델: ${effectiveModelName})...`);
    
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: effectiveModelName });
    const imagePart = imageUrl ? dataUriToGenerativePart(imageUrl) : null;

    const prompt = `
    당신은 전문 SEO 콘텐츠 작가입니다. 제공된 YouTube 영상 스크립트를 종합하여 하나의 블로그 게시물을 생성하고, 반드시 지정된 JSON 형식으로만 응답해야 합니다.

    **입력 스크립트:**\n${transcripts}
    **글쓰기 톤 & 스타일:** ${tone || '친근하고 유익하게'}
    **타겟 독자:** ${audience || '일반 대중'}

    **[매우 중요] 출력 형식:**
    - 당신의 전체 응답은 반드시 아래 구조를 따르는 단일 JSON 객체여야 합니다.
    - JSON 외부에는 어떠한 설명이나 추가 텍스트도 포함해서는 안 됩니다.

    \`\`\`json
    {
      "title": "SEO에 최적화된, 흥미로운 한글 제목",
      "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. 서론, 본론, 결론을 포함해야 합니다.",
      "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요. (예: modern smartphone, user interface, mobile technology)",
      "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용."
    }
    \`\`\`

    **[필수 규칙]**
    1.  **\`content_with_placeholder\` 필드:** 이 필드에 '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다. 이를 누락하면 당신의 응답은 처리될 수 없습니다.
    2.  **HTML 구조:** 본문 내용은 \`<h2>\`, \`<h3>\`, \`<p>\`, \`<ul>\`, \`<li>\` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
    ${imageUrl ? `3. **이미지 문맥:** 제공된 이미지를 분석하여, '[IMAGE_HERE]' 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.` : ''}
    `;
    
    const requestPayload = [prompt];
    if (imagePart) requestPayload.push(imagePart);

    try {
        const result = await model.generateContent(requestPayload);
        const response = await result.response;
        const generatedText = response.text();
        
        console.log(">> Gemini 텍스트 생성 완료! (YouTube 스크립트 기반)");
        return parseGeminiJsonResponse(generatedText);
    } catch (error) {
        console.error(`[오류] Gemini API 호출 중 오류 (YouTube 스크립트 기반): ${error.message}`);
        throw new Error(`Gemini API 오류: ${error.message}`);
    }
}

// --- [Helper 6-2] YouTube 오디오 기반 텍스트 생성 (JSON 출력) ---
async function generateTextFromAudio(apiKey, audioBase64, mimeType, imageUrl, modelName, tone, audience) {
    const effectiveModelName = modelName || "gemini-1.5-pro-latest";
    console.log(`>> Gemini 텍스트 생성 요청 (YouTube 오디오 기반, 모델: ${effectiveModelName})...`);
    
    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: effectiveModelName });

    const audioPart = { inlineData: { data: audioBase64, mimeType } };
    const imagePart = imageUrl ? dataUriToGenerativePart(imageUrl) : null;

    const prompt = `
    당신은 전문 SEO 콘텐츠 작가입니다. 제공된 오디오 파일의 내용을 분석하여 하나의 블로그 게시물을 생성하고, 반드시 지정된 JSON 형식으로만 응답해야 합니다.

    **글쓰기 톤 & 스타일:** ${tone || '친근하고 유익하게'}
    **타겟 독자:** ${audience || '일반 대중'}

    **[매우 중요] 출력 형식:**
    - 당신의 전체 응답은 반드시 아래 구조를 따르는 단일 JSON 객체여야 합니다.
    - JSON 외부에는 어떠한 설명이나 추가 텍스트도 포함해서는 안 됩니다.

    \`\`\`json
    {
      "title": "SEO에 최적화된, 흥미로운 한글 제목",
      "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. 서론, 본론, 결론을 포함해야 합니다.",
      "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요. (예: modern smartphone, user interface, mobile technology)",
      "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용."
    }
    \`\`\`

    **[필수 규칙]**
    1.  **\`content_with_placeholder\` 필드:** 이 필드에 '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다. 이를 누락하면 당신의 응답은 처리될 수 없습니다.
    2.  **HTML 구조:** 본문 내용은 \`<h2>\`, \`<h3>\`, \`<p>\`, \`<ul>\`, \`<li>\` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
    ${imageUrl ? `3. **이미지 문맥:** 제공된 이미지를 분석하여, '[IMAGE_HERE]' 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.` : ''}
    `;

    const requestPayload = [prompt, audioPart];
    if (imagePart) requestPayload.push(imagePart);

    try {
        const result = await model.generateContent(requestPayload);
        const response = await result.response;
        const generatedText = response.text();

        console.log(">> Gemini 텍스트 생성 완료! (YouTube 오디오 기반)");
        return parseGeminiJsonResponse(generatedText);
    } catch (error) {
        console.error(`[오류] Gemini API 호출 중 오류 (YouTube 오디오 기반): ${error.message}`);
        throw new Error(`Gemini API 오류: ${error.message}`);
    }
}

// --- [Helper 6-3] 업로드된 동영상 기반 텍스트 생성 (JSON 출력) - 수정됨 ---
async function generateTextFromVideo(apiKey, videoFile, topic, imageUrl, modelName, tone, audience) {
    const effectiveModelName = modelName || "gemini-1.5-pro-latest";
    console.log(`>> Gemini 텍스트 생성 요청 (동영상 파일 기반, 모델: ${effectiveModelName})...`);
    
    const genAIClient = new GoogleGenerativeAI(apiKey);
    let uploadedFile = null;

    try {
        console.log(`>> Gemini File API에 동영상 업로드 중: ${videoFile.path} (MIME: ${videoFile.mimetype})`);
        const uploadResult = await genAIClient.uploadFile(videoFile.path, {
            mimeType: videoFile.mimetype,
            displayName: videoFile.originalname,
        });
        uploadedFile = uploadResult.file;
        console.log(`>> Gemini File API 업로드 완료: ${uploadedFile.name}`);

        const model = genAIClient.getGenerativeModel({ model: effectiveModelName });
        
        const imagePart = imageUrl ? dataUriToGenerativePart(imageUrl) : null;
        const prompt = `
        당신은 전문 SEO 콘텐츠 작가입니다. 제공된 동영상 파일의 내용을 분석하고, 주어진 주제에 맞춰 하나의 블로그 게시물을 생성하고, 반드시 지정된 JSON 형식으로만 응답해야 합니다.

        **분석할 주제:** ${topic}
        **글쓰기 톤 & 스타일:** ${tone || '친근하고 유익하게'}
        **타겟 독자:** ${audience || '일반 대중'}

        **[매우 중요] 출력 형식:**
        - 당신의 전체 응답은 반드시 아래 구조를 따르는 단일 JSON 객체여야 합니다.
        - JSON 외부에는 어떠한 설명이나 추가 텍스트도 포함해서는 안 됩니다.

        \`\`\`json
        {
          "title": "SEO에 최적화된, 흥미로운 한글 제목",
          "content_with_placeholder": "본문의 내용과 흐름을 고려하여, 이미지가 들어갈 가장 적절한 위치에 '[IMAGE_HERE]' 라는 문자열을 **반드시 단 한 번만 포함**시킨 전체 글 내용. 서론, 본론, 결론을 포함해야 합니다.",
          "image_search_keywords": "블로그 글의 핵심 내용을 가장 잘 나타내는, Pexels에서 검색할 **영어 검색어 목록**. 쉼표(,)로 구분된 3-4개의 키워드를 제공해주세요. (예: modern smartphone, user interface, mobile technology)",
          "summary": "블로그 글의 내용을 1~2 문장으로 요약한 내용."
        }
        \`\`\`

        **[필수 규칙]**
        1.  **\`content_with_placeholder\` 필드:** 이 필드에 '[IMAGE_HERE]'를 포함하는 것은 선택이 아닌 **필수 요구사항**입니다. 이를 누락하면 당신의 응답은 처리될 수 없습니다.
        2.  **HTML 구조:** 본문 내용은 \`<h2>\`, \`<h3>\`, \`<p>\`, \`<ul>\`, \`<li>\` 등의 태그를 사용하여 의미적으로 구조화해야 합니다.
        ${imageUrl ? `3. **이미지 문맥:** 제공된 이미지를 분석하여, '[IMAGE_HERE]' 플레이스홀더를 이미지 내용과 가장 관련이 깊은 문단 바로 뒤에 배치해야 합니다.` : ''}
        `;

        const requestPayload = [prompt, { "fileData": { "mimeType": uploadedFile.mimeType, "fileUri": uploadedFile.uri } }];
        if (imagePart) requestPayload.push(imagePart);

        const result = await model.generateContent(requestPayload);
        const response = await result.response;
        const generatedText = response.text();

        console.log(">> Gemini 텍스트 생성 완료! (동영상 파일 기반)");
        return parseGeminiJsonResponse(generatedText);

    } catch (error) {
        console.error(`[오류] Gemini API 호출 중 오류 (동영상 파일 기반): ${error.message}`);
        throw new Error(`Gemini API 오류: ${error.message}`);
    } finally {
        if (uploadedFile) {
            await genAIClient.deleteFile(uploadedFile.name);
            console.log(`>> Gemini File API에서 파일 정리/삭제 완료: ${uploadedFile.name}`);
        }
    }
}


// --- API 엔드포인트 ---

// Gemini 주제 탐색 엔드포인트
app.post('/chat-for-topic', async (req, res) => {
    const { apiKey, message } = req.body;
    console.log(`[/chat-for-topic] 요청 수신 (모델: Gemini)...`);

    if (!apiKey || !message) {
        return res.status(400).json({ error: "Gemini API 키와 메시지는 필수입니다." });
    }

    try {
        const genAI = new GoogleGenerativeAI(apiKey);
        const model = genAI.getGenerativeModel({ model: "gemini-pro" });

        const prompt = `당신은 사용자가 블로그 포스팅 주제를 찾도록 돕는 창의적인 어시스턴트입니다. 사용자와 대화하며 아이디어를 브레인스토밍하고, 흥미로운 주제를 제안해주세요. 답변은 친근하고 간결하게 한글로 해주세요. 사용자의 현재 메시지: "${message}"`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const aiResponse = response.text();

        console.log('>> Gemini (chat) 응답 생성 완료!');
        res.json({ reply: aiResponse });
    } catch (error) {
        console.error(`[치명적 오류] /chat-for-topic 처리 중: ${error.stack}`);
        const errorMessage = error.message || "알 수 없는 오류";
        res.status(500).json({ error: `Gemini API 오류: ${errorMessage}` });
    }
});

// 주제 기반 포스트 생성 엔드포인트
app.post('/generate-post', async (req, res) => {
    const { apiKey, topic, imageSource, aiImageModel, gcpProjectId, pexelsApiKey, accessToken, modelName, tone, audience, uploadedImageUri } = req.body;
    console.log(`[/generate-post] 요청 수신: ${topic}, 이미지 소스: ${imageSource}, 콘텐츠 모델: ${modelName}`);

    if (!apiKey || !topic) {
        return res.status(400).json({ error: "Gemini API 키와 주제는 필수입니다." });
    }

    try {
        const generatedData = await generateTextContent(apiKey, topic, uploadedImageUri, modelName, tone, audience);
        const { title, content_with_placeholder, image_search_keywords } = generatedData;

        let imageUrl = uploadedImageUri;
        if (!imageUrl && imageSource !== 'none') {
            if (imageSource === 'ai') {
                imageUrl = await generateAiImage(gcpProjectId, topic, accessToken);
            } else if (imageSource === 'pexels') {
                const keywordsArray = image_search_keywords.split(',').map(k => k.trim());
                imageUrl = await fetchImageFromPexels(keywordsArray, pexelsApiKey);
            }
        }

        if (!imageUrl && imageSource !== 'none' && imageSource !== 'upload') {
            console.warn(`[최종 경고] '${imageSource}' 소스에서 이미지를 가져오는 데 실패했습니다. 이미지 없이 포스트를 생성합니다.`);
        }
        
        const seoFilename = image_search_keywords ? image_search_keywords.split(',')[0].trim().replace(/\s+/g, '-') : title.substring(0, 20).replace(/\s+/g, '-');
        const finalBody = insertImageIntoHtml(content_with_placeholder, imageUrl, seoFilename, title);

        res.json({ title, body: finalBody, keywords: image_search_keywords });

    } catch (error) {
        console.error(`[치명적 오류] /generate-post 처리 중: ${error.stack}`);
        res.status(500).json({ error: error.message });
    }
});

// YouTube 기반 포스트 생성 엔드포인트
app.post('/generate-post-from-youtube', async (req, res) => {
    const { urls, apiKey, imageSource, aiImageModel, gcpProjectId, pexelsApiKey, accessToken, modelName, tone, audience, uploadedImageUri, youtubeSourceType } = req.body;
    console.log(`[/generate-post-from-youtube] 요청 수신: ${urls.length}개의 영상, 소스 타입: ${youtubeSourceType}, 이미지 소스: ${imageSource}`);

    if (!apiKey || !urls || urls.length === 0) {
        return res.status(400).json({ error: "Gemini API 키와 하나 이상의 YouTube URL은 필수입니다." });
    }
    
    if (youtubeSourceType === 'audio' && urls.length > 1) {
        return res.status(400).json({ error: "음성 분석은 한 번에 하나의 YouTube URL만 지원합니다." });
    }

    try {
        let generatedData;
        
        if (youtubeSourceType === 'audio') {
            const { audioBase64, mimeType } = await fetchAudioAsBase64(urls[0]);
            generatedData = await generateTextFromAudio(apiKey, audioBase64, mimeType, uploadedImageUri, modelName, tone, audience);
        } else { // 'transcript'
            const transcripts = await fetchAndCombineTranscripts(urls);
            if (!transcripts) {
                return res.status(400).json({ error: "제공된 URL에서 유효한 스크립트를 추출할 수 없었습니다. 영상에 자막이 있는지, URL이 올바른지 확인해주세요." });
            }
            generatedData = await generateTextFromTranscripts(apiKey, transcripts, uploadedImageUri, modelName, tone, audience);
        }
        
        const { title, content_with_placeholder, image_search_keywords } = generatedData;

        let imageUrl = uploadedImageUri;
        if (!imageUrl && imageSource !== 'none') {
            if (imageSource === 'ai') {
                imageUrl = await generateAiImage(gcpProjectId, title, accessToken);
            } else if (imageSource === 'pexels') {
                const keywordsArray = image_search_keywords.split(',').map(k => k.trim());
                imageUrl = await fetchImageFromPexels(keywordsArray, pexelsApiKey);
            }
        }

        if (!imageUrl && imageSource !== 'none' && imageSource !== 'upload') {
            console.warn(`[최종 경고] '${imageSource}' 소스에서 이미지를 가져오는 데 실패했습니다. 이미지 없이 포스트를 생성합니다.`);
        }

        const seoFilename = image_search_keywords ? image_search_keywords.split(',')[0].trim().replace(/\s+/g, '-') : title.substring(0, 20).replace(/\s+/g, '-');
        const finalBody = insertImageIntoHtml(content_with_placeholder, imageUrl, seoFilename, title);

        res.json({ title, body: finalBody, keywords: image_search_keywords });

    } catch (error) {
        console.error(`[치명적 오류] /generate-post-from-youtube 처리 중: ${error.stack}`);
        res.status(500).json({ error: error.message });
    }
});

// [신규] 동영상 파일 기반 포스트 생성 엔드포인트
app.post('/generate-post-from-video', upload.single('video'), async (req, res) => {
    const { apiKey, topic, imageSource, aiImageModel, gcpProjectId, pexelsApiKey, accessToken, modelName, tone, audience, uploadedImageUri } = req.body;
    const videoFile = req.file;
    console.log(`[/generate-post-from-video] 요청 수신: ${topic}, 파일: ${videoFile.originalname}, 이미지 소스: ${imageSource}`);

    if (!apiKey || !topic || !videoFile) {
        return res.status(400).json({ error: "API 키, 주제, 동영상 파일은 필수입니다." });
    }

    try {
        const generatedData = await generateTextFromVideo(apiKey, videoFile, topic, uploadedImageUri, modelName, tone, audience);
        const { title, content_with_placeholder, image_search_keywords } = generatedData;

        let imageUrl = uploadedImageUri;
        if (!imageUrl && imageSource !== 'none') {
            if (imageSource === 'ai') {
                imageUrl = await generateAiImage(gcpProjectId, title, accessToken);
            } else if (imageSource === 'pexels') {
                const keywordsArray = image_search_keywords.split(',').map(k => k.trim());
                imageUrl = await fetchImageFromPexels(keywordsArray, pexelsApiKey);
            }
        }
        
        if (!imageUrl && imageSource !== 'none' && imageSource !== 'upload') {
            console.warn(`[최종 경고] '${imageSource}' 소스에서 이미지를 가져오는 데 실패했습니다. 이미지 없이 포스트를 생성합니다.`);
        }

        const seoFilename = image_search_keywords ? image_search_keywords.split(',')[0].trim().replace(/\s+/g, '-') : title.substring(0, 20).replace(/\s+/g, '-');
        const finalBody = insertImageIntoHtml(content_with_placeholder, imageUrl, seoFilename, title);

        res.json({ title, body: finalBody, keywords: image_search_keywords });

    } catch (error) {
        console.error(`[치명적 오류] /generate-post-from-video 처리 중: ${error.stack}`);
        res.status(500).json({ error: error.message });
    } finally {
        if (videoFile && videoFile.path) {
            fs.unlink(videoFile.path, (err) => {
                if (err) console.error(`[오류] 임시 동영상 파일 삭제 실패: ${videoFile.path}`, err);
                else console.log(`>> 임시 동영상 파일 삭제 완료: ${videoFile.path}`);
            });
        }
    }
});


// --- Auto Shutdown Endpoints (Windows Only) ---
app.post('/shutdown-pc', (req, res) => {
    if (process.platform !== 'win32') {
        const msg = "자동 종료 기능은 Windows에서만 지원됩니다.";
        console.warn(`[경고] /shutdown-pc: ${msg}`);
        return res.status(400).json({ error: msg });
    }
    const { delay } = req.body;
    if (!delay || isNaN(parseInt(delay))) {
        return res.status(400).json({ error: "유효한 지연 시간(초)이 필요합니다." });
    }
    const delayInSeconds = parseInt(delay);
    console.log(`>> PC 종료 명령 수신 (${delayInSeconds}초 후)...`);
    exec(`shutdown /s /t ${delayInSeconds}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`[오류] Shutdown 실행 실패: ${error.message}`);
            return res.status(500).json({ error: `Shutdown command failed: ${error.message}` });
        }
        if (stderr) {
            console.warn(`[정보] Shutdown stderr: ${stderr}`);
        }
        console.log(`>> Shutdown stdout: ${stdout}`);
        res.status(200).json({ message: "Shutdown command issued successfully." });
    });
});

app.post('/cancel-shutdown', (req, res) => {
    if (process.platform !== 'win32') {
        const msg = "자동 종료 기능은 Windows에서만 지원됩니다.";
        console.warn(`[경고] /cancel-shutdown: ${msg}`);
        return res.status(400).json({ error: msg });
    }
    console.log(">> PC 종료 취소 명령 수신...");
    exec('shutdown /a', (error, stdout, stderr) => {
        if (error && !stderr.includes('No system shutdown is in progress')) {
            console.error(`[오류] Shutdown cancellation 실패: ${error.message}`);
            return res.status(500).json({ error: `Shutdown cancellation command failed: ${error.message}` });
        }
        if (stderr) {
            console.warn(`[정보] Shutdown cancellation stderr: ${stderr}`);
        }
        console.log(`>> Shutdown cancellation stdout: ${stdout}`);
        res.status(200).json({ message: "Shutdown cancellation issued successfully." });
    });
});


app.listen(PORT, () => {
    console.log(`--- 🚀 AI Auto-Blogging Node.js 백엔드 서버 시작 (포트: ${PORT}) ---`);
    console.log(`--- 🌐 이제 브라우저에서 http://localhost:${PORT} 주소로 접속하세요. ---`);
});
