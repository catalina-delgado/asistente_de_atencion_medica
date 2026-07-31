const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const API_TOKEN = import.meta.env.VITE_API_TOKEN

export interface ChatResponse {
  sessionId: string
  respuesta: string
  preguntasSeguimiento: string[]
  listoParaTriage: boolean
  turno: number
}

interface ApiErrorBody {
  error?: { code?: string; message?: string; requestId?: string }
}

export async function enviarMensaje(mensaje: string, sessionId: string | null): Promise<ChatResponse> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
      },
      body: JSON.stringify({ sessionId, mensaje }),
    })
  } catch {
    // El fetch en sí falló: el backend no respondió (no está corriendo, CORS, red).
    throw new Error('No se pudo contactar al backend. Verifica que esté corriendo.')
  }

  if (!res.ok) {
    // El backend sí respondió, pero con un error (ej. el modelo de IA no
    // disponible). Usamos el mensaje que ya viene armado desde el backend
    // (ver app/utils/errors.py) en vez de un texto genérico.
    let mensajeError = `Error del servidor (${res.status})`
    try {
      const body: ApiErrorBody = await res.json()
      if (body.error?.message) {
        mensajeError = body.error.message
      }
    } catch {
      // El cuerpo no era JSON; nos quedamos con el mensaje genérico de arriba.
    }
    throw new Error(mensajeError)
  }

  return res.json()
}
