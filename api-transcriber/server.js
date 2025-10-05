import express from "express";
import fs from "fs";
import path from "path";
import dotenv from "dotenv";
import Groq from "groq-sdk";
import ffmpeg from "fluent-ffmpeg";
import ffmpegStatic from "ffmpeg-static";

dotenv.config();

const GROQ_KEY = process.env.GROQ_KEY;
if (!GROQ_KEY || GROQ_KEY === "nasasapceChalleng") {
  console.error(
    "GROQ_KEY ausente ou inválida. Defina a variável de ambiente GROQ_KEY com sua chave da Groq (veja .env)."
  );
  process.exit(1);
}

const app = express();
app.use(express.json({ limit: "100mb" })); // permite grandes base64

const groq = new Groq({ apiKey: GROQ_KEY });
ffmpeg.setFfmpegPath(ffmpegStatic);

app.post("/transcribe", async (req, res) => {
  try {
    const { audioBase64 } = req.body;

    if (!audioBase64) {
      return res
        .status(400)
        .json({ sucesso: false, erro: "Parâmetro 'audioBase64' ausente" });
    }

    // cria um arquivo temporário único
    const tempDir = "uploads";
    if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir);
    const tempFilePath = path.join(tempDir, `audio_${Date.now()}.input`);
    const tempMp3Path = tempFilePath + ".converted.mp3";

    // remove prefixo do base64, se existir (ex: data:audio/wav;base64,...)
    const base64Data = audioBase64.replace(/^data:audio\/\w+;base64,/, "");

    // grava o buffer decodificado em disco
    fs.writeFileSync(tempFilePath, Buffer.from(base64Data, "base64"));

    // converte para mp3 usando ffmpeg
    await new Promise((resolve, reject) => {
      ffmpeg(tempFilePath)
        .toFormat("mp3")
        .on("error", (err) => {
          console.error("Erro na conversão ffmpeg:", err.message);
          reject(err);
        })
        .on("end", () => resolve())
        .save(tempMp3Path);
    });

    // envia o arquivo convertido para o modelo Whisper
    const response = await groq.audio.transcriptions.create({
      file: fs.createReadStream(tempMp3Path),
      model: "whisper-large-v3-turbo",
    });

    // remove arquivos temporários
    try {
      if (fs.existsSync(tempFilePath)) fs.unlinkSync(tempFilePath);
      if (fs.existsSync(tempMp3Path)) fs.unlinkSync(tempMp3Path);
    } catch (e) {
      console.warn("Não foi possível remover arquivo temporário:", e.message);
    }

    res.json({
      sucesso: true,
      texto: response.text,
    });
  } catch (err) {
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
