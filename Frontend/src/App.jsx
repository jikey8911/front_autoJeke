import { useEffect, useState } from 'react';
import { initNeural, NeoCard } from '@jikey8911/jeikei-ui';

function App() {
  const [agents, setAgents] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Inicializar fondo neuronal
    const canvas = document.getElementById("neural");
    if (canvas) {
      initNeural(canvas);
    }

    // Consultar estado de los agentes al backend
    const fetchAgents = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://163.192.114.190:5000';
        const response = await fetch(`${apiUrl}/agents`);
        const data = await response.json();
        setAgents(data);
      } catch (error) {
        console.error("Error fetching agents:", error);
        setAgents({ error: "Fallo al conectar con Backend" });
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-start overflow-hidden bg-neo-bg py-10">
      {/* Fondo de Red Neuronal */}
      <canvas id="neural" className="fixed inset-0 z-0 opacity-40 pointer-events-none" />

      <div className="z-10 text-center space-y-8 p-4 w-full max-w-5xl">
        <h1 className="text-5xl md:text-7xl font-bold text-glow-cyan uppercase tracking-widest text-neo-cyan drop-shadow-md">
          AutomataJeiKei
        </h1>
        <p className="text-neo-cyan/70 tracking-widest uppercase text-sm font-bold">
          Sistema Operativo Autónomo de Negocios
        </p>

        {/* Panel principal de estado de agentes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-8 w-full text-left">
          
          {/* Card de Estado General */}
          <NeoCard
            title="SYSTEM LINK"
            value={loading ? "CONNECTING..." : (agents?.error ? "ERROR" : "ONLINE")}
            status={loading ? "FETCHING AGENT DATA" : "CONNECTION ESTABLISHED"}
            variant={agents?.error ? "magenta" : "cyan"}
          />

          {/* Card de Respuesta de Agentes */}
          <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm overflow-hidden flex flex-col">
            <h3 className="text-neo-cyan font-bold tracking-widest mb-2 border-b border-neo-cyan/30 pb-2">
              AGENT TELEMETRY (RAW)
            </h3>
            <div className="flex-1 overflow-y-auto max-h-48 text-xs text-neo-cyan/80 font-mono whitespace-pre-wrap">
              {loading ? (
                <span className="animate-pulse">Cargando datos de agentes...</span>
              ) : (
                JSON.stringify(agents, null, 2)
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}

export default App;