# FinTech Multi-Agent Support System

Sistema multi-agente para soporte al cliente de banca digital, construido con
Anthropic Claude (El proyecto se subió a git solo cuando todo estaba funcionando).

## Arquitectura

```
Usuario → [Router Agent] → [Worker Specialist] → [Synthesizer] → Respuesta
```

### Agentes

| Agente | Rol | Herramientas |
|--------|-----|-------------|
| **Router** | Clasifica la intención del usuario y delega | get_account |
| **Worker 1: Soporte y Tarifas** | Consultas sobre tarifas, comisiones y FAQ | get_account, get_rates, get_faq |
| **Worker 2: Seguridad y Fraudes** | Políticas de seguridad, bloqueo de cuentas | get_account, get_security_policies, block_account |
| **Worker 3: Legal y Privacidad** | Términos legales y protección de datos | get_account, get_legal_terms, get_privacy_policy |
| **Synthesizer** | Combina resultados en respuesta final | (ninguna) |

### Flujo de Trabajo

1. El usuario envía un mensaje
2. **Router Agent** clasifica la intención (RATES_AND_SUPPORT, SECURITY_AND_FRAUD, LEGAL_AND_PRIVACY, GENERAL)
3. El **Worker Specialist** correspondiente procesa la consulta usando RAG sobre la documentación
4. **Synthesizer Agent** combina los hallazgos en una respuesta coherente
5. La respuesta se envía al usuario

## Estructura del Proyecto

```
one_proyect/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Servidor FastAPI + frontend web
│   │   ├── config.py              # Configuración de entorno
│   │   ├── mock_data.py           # Datos de documentación financiera
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py      # Clase base de agente
│   │   │   ├── router.py          # Agente enrutador
│   │   │   ├── worker_support.py  # Worker 1: Tarifas y FAQ
│   │   │   ├── worker_security.py # Worker 2: Seguridad y Fraudes
│   │   │   ├── worker_legal.py    # Worker 3: Legal y Privacidad
│   │   │   └── synthesizer.py     # Síntesis de respuestas
│   │   ├── core/
│   │   │   ├── session_state.py   # Estado de sesión (patrón Claude-final)
│   │   │   ├── error_handler.py   # Manejo estructurado de errores
│   │   │   └── tool_executor.py   # Ejecutor de herramientas
│   │   ├── mcp/
│   │   │   └── document_server.py # Servidor MCP de documentos
│   │   └── tools/
│   │       └── bank_tools.py      # Herramientas bancarias simuladas
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── data/
│   └── documentacion_fintech.pdf  # Documentación fuente
├── docker-compose.yml
└── README.md
```

## Requisitos

- Python 3.11+
- Docker y Docker Compose (para despliegue)
- API key de Anthropic

## Configuración

1. Clonar el repositorio:
   ```bash
   git clone <repo-url> one_proyect
   cd one_proyect
   ```

2. Configurar variables de entorno:
   ```bash
   cp backend/.env.example backend/.env
   # Editar backend/.env y agregar ANTHROPIC_API_KEY
   ```

3. Ejecutar con Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Acceder a la interfaz web:
   ```
   http://localhost:8000
   ```
## Ejemplo preguntas al agente.
1.
 ```
   "Hi, I'm Sarah Chen. I would like to know if they are going to charge me anything to change my debit card that broke, and also if my account has any cashback benefits."
   ```
 ```
   "You must inform them in detail that as a Premium customer, the card replacement fee is $0.00 and that they have an active benefit of 1% Cashback along with travel assistance and priority support."
   ```

2.
    ```
   "Please help! I just saw a strange movement in my account in my app that I didn't make. I think my account was hacked or someone cloned my card. What do I do so they don't steal my money?"
   ```
  ```
   "I'm sorry to hear this. To protect your funds, I have proceeded to place a preventative lock on your account immediately under our Zero Liability policy. You have a period of 24 hours for your responsibility to be $0..."
   ```

3.
   ```
  "Hello, I'm James Okafor. I'm trying to send an emergency transfer to my brother who is out of the country but the platform won't let me. What is my daily limit for international transfers to be able to send it now?"
   ```
     ```
  "We detected that your account has an active restriction for international shipments due to internal verification policies. Please contact our support line..."
   ```

## Desarrollo Local

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Ejecutar servidor:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

## Despliegue en Oracle Cloud (OSI)

1. Construir la imagen Docker:
   ```bash
   docker build -t fintech-multi-agent ./backend
   ```

2. Etiquetar para Oracle Container Registry:
   ```bash
   docker tag fintech-multi-agent <region>.ocir.io/<namespace>/fintech-multi-agent:latest
   ```

3. Subir a OCI:
   ```bash
   docker push <region>.ocir.io/<namespace>/fintech-multi-agent:latest
   ```

4. Desplegar en OCI Container Instance o Kubernetes:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz web de chat |
| `/chat` | POST | Enviar mensaje al sistema multi-agente |
| `/health` | GET | Health check |
| `/session/{id}` | GET | Estado de sesión (debug) |

### Ejemplo de Uso de la API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuáles son las tarifas para una cuenta premium?"}'
```

## Pruebas

Para ejecutar pruebas de escenario:
```bash
cd backend
python -m pytest tests/
```

## Referencias

- Arquitectura de agentes: Anthropic Claude + FastAPI
- Protocolo MCP para acceso a documentación
