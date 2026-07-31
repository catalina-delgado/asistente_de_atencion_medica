import { useState, type FormEvent } from 'react'
import { enviarMensaje } from './api'
import './App.css'

interface Turno {
  autor: 'usuario' | 'asistente'
  texto: string
}

function App() {
  const [mensajes, setMensajes] = useState<Turno[]>([
    { autor: 'asistente', texto: 'Hola, soy el asistente de Emermédica. Cuéntame qué síntomas tienes.' },
  ])
  const [entrada, setEntrada] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const texto = entrada.trim()
    if (!texto || cargando) return

    setMensajes((prev) => [...prev, { autor: 'usuario', texto }])
    setEntrada('')
    setCargando(true)
    setError(null)

    try {
      const respuesta = await enviarMensaje(texto, sessionId)
      setSessionId(respuesta.sessionId)
      setMensajes((prev) => {
        const nuevos: Turno[] = [...prev, { autor: 'asistente', texto: respuesta.respuesta }]
        if (respuesta.preguntasSeguimiento.length > 0) {
          nuevos.push({
            autor: 'asistente',
            texto: respuesta.preguntasSeguimiento.map((p, i) => `${i + 1}. ${p}`).join('\n'),
          })
        }
        return nuevos
      })
    } catch {
      setError('No se pudo contactar al asistente. Verifica que el backend esté corriendo.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Emermédica · Asistente de Atención Médica</h1>
      </header>

      <main className="chat">
        {mensajes.map((m, i) => (
          <div key={i} className={`bubble ${m.autor}`}>
            {m.texto}
          </div>
        ))}
        {cargando && <div className="bubble asistente">Escribiendo…</div>}
        {error && <div className="bubble error">{error}</div>}
      </main>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          placeholder="Describe tus síntomas…"
          disabled={cargando}
        />
        <button type="submit" disabled={cargando || !entrada.trim()}>
          Enviar
        </button>
      </form>
    </div>
  )
}

export default App
