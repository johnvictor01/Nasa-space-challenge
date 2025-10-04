import express from "express";
import multer from "multer";
import fs from "fs";
import dotenv from "dotenv";
import Groq from "groq-sdk";

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

app.post("/transcribe", upload.single("audio"), async (req, res) => {
  try {
    const filePath = req.file.path;

    const response = await groq.audio.transcriptions.create({
      file: fs.createReadStream(filePath),
      model: "whisper-large-v3-turbo",
    });

    fs.unlinkSync(filePath); // remove o arquivo temporário

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
