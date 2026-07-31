const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const API_TOKEN = import.meta.env.VITE_API_TOKEN

export interface ChatResponse {
  sessionId: string
  respuesta: string
  preguntasSeguimiento: string[]
  listoParaTriage: boolean
  turno: number
}

export async function enviarMensaje(mensaje: string, sessionId: string | null): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
    },
    body: JSON.stringify({ sessionId, mensaje }),
  })

  if (!res.ok) {
    throw new Error(`Error del servidor (${res.status})`)
  }

  return res.json()
}
