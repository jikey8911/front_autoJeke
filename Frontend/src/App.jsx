import { useEffect, useState } from 'react';
import { initNeural, NeoCard, NeoButton } from '@jikey8911/jeikei-ui';

function App() {
  const [data, setData] = useState({
    estado_sistema: "...",
    estado_gateway: "...",
    balance: { global: 0.0, uaes: [] },
    agentes_globales: [],
    uaes: { activas: 0, inactivas: 0, duplicadas: 0, muertas: 0 },
    oportunidades_globales: 0
  });
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("CHECKING...");

  const fetchAllData = async () => {
    setLoading(true);
    setBackendStatus("SYNCING...");
    try {
      // ÚNICA PETICIÓN: Eliminamos todas las peticiones a /status, /agents, /test_ws, etc.
      const response = await fetch('/api/all');
      if (response.ok) {
        const jsonResponse = await response.json();
        console.log("[Frontend] Respuesta de /api/all:", jsonResponse); // NUEVO: Log para depuración
        setData(jsonResponse);
        setBackendStatus("CONNECTED");
      } else {
        setBackendStatus(`FAILED: ${response.status}`);
      }
    } catch (error) {
      console.error("[Frontend] Error al obtener /all:", error);
      setBackendStatus(`FAILED: ${error.message}`);
    }
    setLoading(false);
  };

  useEffect(() => {
    const canvas = document.getElementById("neural");
    if (canvas) initNeural(canvas);
    
    // Solo llamamos a la función centralizada una vez al cargar
    fetchAllData();
  }, []);

  const renderList = (title, items) => (
    <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm flex flex-col h-full">
      <h3 className="text-neo-cyan font-bold tracking-widest mb-2 border-b border-neo-cyan/30 pb-2 uppercase text-xs">
        {title}
      </h3>
      <div className="flex-1 overflow-y-auto max-h-40 text-sm text-neo-cyan/80 font-mono">
        {items && items.length > 0 ? (
          <ul className="list-disc list-inside">
            {items.map((item, idx) => (
              <li key={idx}>{typeof item === 'object' ? `${item.id} - $${item.balance}` : item}</li>
            ))}
          </ul>
        ) : (
          <span>No hay datos.</span>
        )}
      </div>
    </div>
  );

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-start overflow-x-hidden bg-neo-bg py-10 text-neo-cyan">
      <canvas id="neural" className="fixed inset-0 z-0 opacity-40 pointer-events-none" />

      <div className="z-10 text-center space-y-8 p-4 w-full max-w-7xl">
        <h1 className="text-5xl md:text-7xl font-bold text-glow-cyan uppercase tracking-widest drop-shadow-md">
          Omni-Revenue
        </h1>
        <p className="text-neo-cyan/70 tracking-widest uppercase text-sm font-bold">
          Sistema Operativo Autónomo de Negocios
        </p>

        <div className="flex flex-col items-center justify-center space-y-4 pb-4">
          <NeoButton variant="cyan" onClick={fetchAllData}>
            {loading ? "SYNCING..." : "FORCE SYNC DATA"}
          </NeoButton>
          <div className="text-xs font-mono text-neo-cyan/60 uppercase">
            Backend API Link: <span className={backendStatus === "CONNECTED" ? "text-neo-cyan" : "text-neo-magenta"}>{backendStatus}</span>
          </div>
        </div>

        {/* HUD de Datos Consolidados */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full text-left">
          <NeoCard title="ESTADO SISTEMA" value={loading ? "..." : data.estado_sistema} status="KERNEL" variant="cyan" />
          <NeoCard title="BALANCE GLOBAL" value={loading ? "..." : `$${data.balance.global}`} status="USDT" variant="amber" />
          <NeoCard title="OPORTUNIDADES" value={loading ? "..." : data.oportunidades_globales} status="DETECTADAS" variant="magenta" />
          <NeoCard title="ESTADO GATEWAY" value={loading ? "..." : data.estado_gateway} status="CONEXIÓN" variant="cyan" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 w-full text-left">
          <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm flex flex-col">
             <h3 className="text-neo-cyan font-bold tracking-widest mb-4 border-b border-neo-cyan/30 pb-2 uppercase text-xs">
                Resumen UAEs
             </h3>
             <div className="flex justify-between items-center py-1">
                <span className="text-neo-cyan/80">Activas:</span>
                <span className="font-bold text-neo-cyan">{data.uaes.activas}</span>
             </div>
             <div className="flex justify-between items-center py-1">
                <span className="text-neo-cyan/80">Inactivas:</span>
                <span className="font-bold text-neo-amber">{data.uaes.inactivas}</span>
             </div>
             <div className="flex justify-between items-center py-1">
                <span className="text-neo-cyan/80">Duplicadas:</span>
                <span className="font-bold text-neo-cyan">{data.uaes.duplicadas}</span>
             </div>
             <div className="flex justify-between items-center py-1">
                <span className="text-neo-cyan/80">Muertas:</span>
                <span className="font-bold text-neo-magenta">{data.uaes.muertas}</span>
             </div>
          </div>

          {renderList("Agentes Globales (The Core)", data.agentes_globales)}
          {renderList("Balances por UAE", data.balance.uaes)}
        </div>
      </div>
    </div>
  );
}

export default App;
