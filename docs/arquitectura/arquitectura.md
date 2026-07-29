# Arquitectura del Backend

## Objetivo

El backend implementa una arquitectura modular basada en responsabilidades separadas para facilitar el mantenimiento, escalabilidad y pruebas.

## Componentes

### API

Expone los endpoints REST del sistema.

Actualmente:

- POST /chat
- POST /triage
- POST /attention

No contiene lógica de negocio.

---

### Services

Implementa toda la lógica del sistema.

Ejemplos:

- Gestión del chat
- Extracción de síntomas
- Clasificación de triaje
- Creación de atención

---

### Clinical

Contiene exclusivamente reglas médicas.

No depende del modelo LLM.

Ejemplos

- Banderas rojas
- Niveles de triaje
- Catálogo de síntomas

---

### LLM

Abstrae la interacción con el modelo de lenguaje.

Permite cambiar GPT por Llama, Claude o cualquier otro modelo sin modificar el resto del sistema.

---

### Repositories

Acceso a la base de datos.

Los servicios nunca interactúan directamente con PostgreSQL.

---

### Schemas

Modelos Pydantic para requests y responses.

---

### Models

Entidades del dominio.

---

### Database

Configuración de SQLAlchemy y conexión.

---

## Flujo general

Usuario

↓

API

↓

Service

↓

Clinical + LLM

↓

Repository

↓

Base de datos