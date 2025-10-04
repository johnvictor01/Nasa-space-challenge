import express from "express";
import multer from "multer";
import fs from "fs";
import path from "path";
import dotenv from "dotenv";
import Groq from "groq-sdk";
import ffmpeg from "fluent-ffmpeg";
import ffmpegStatic from "ffmpeg-static";

dotenv.config();
// valida variável de ambiente da chave da API para falhas rápidas na inicialização
const GROQ_KEY = process.env.GROQ_KEY;
if (!GROQ_KEY || GROQ_KEY === "nasasapceChalleng") {
  console.error(
    "GROQ_KEY ausente ou inválida. Defina a variável de ambiente GROQ_KEY com sua chave da Groq (veja .env)."
  );
  process.exit(1);
}

const app = express();
const upload = multer({ dest: "uploads/" });
const groq = new Groq({ apiKey: GROQ_KEY });

// configura o caminho do binário ffmpeg fornecido por ffmpeg-static
ffmpeg.setFfmpegPath(ffmpegStatic);

app.post("/transcribe", upload.single("audio"), async (req, res) => {
  try {
    const filePath = req.file.path;

    // Converter qualquer áudio recebido para MP3 usando ffmpeg
    const tempMp3Path = filePath + ".converted.mp3";
    await new Promise((resolve, reject) => {
      ffmpeg(filePath)
        .toFormat("mp3")
        .on("error", (err) => {
          console.error("Erro na conversão ffmpeg:", err.message);
          reject(err);
        })
        .on("end", () => resolve())
        .save(tempMp3Path);
    });

    const response = await groq.audio.transcriptions.create({
      file: fs.createReadStream(tempMp3Path),
      model: "whisper-large-v3-turbo",
    });

    // remove arquivos temporários (original e convertido)
    try {
      if (fs.existsSync(tempMp3Path)) fs.unlinkSync(tempMp3Path);
      if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    } catch (e) {
      console.warn("Não foi possível remover arquivo temporário:", e.message);
    }

    res.json({
      sucesso: true,
      texto: response.text,
    });
  } catch (err) {
    // se a chamada à API retornar 401, propague um erro mais claro
    const status = err?.response?.status || err?.status || 500;
    const message =
      status === 401
        ? "401 Unauthorized - chave de API inválida ou não autorizada"
        : err.message || String(err);

    console.error("Erro na transcrição (status", status + "):", err);
    res.status(status).json({ sucesso: false, erro: message });
  }
});

app.listen(process.env.PORT || 3000, () =>
  console.log(`Servidor em http://localhost:${process.env.PORT || 3000}`)
);

console.log("GROQ_KEY:", process.env.GROQ_KEY);
