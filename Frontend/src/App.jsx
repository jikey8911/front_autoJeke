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
      // FORZAMOS RUTA RELATIVA ESTRICTA: El navegador pedirá a la misma IP y puerto 3000
      // Vite Middleware recibirá /api/all y lo pasará al backend:5000 internamente.
      const response = await fetch('/api/all', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const jsonResponse = await response.json();
        console.log("[Frontend] Response /api/all:", jsonResponse);
        setData(jsonResponse);
        setBackendStatus("CONNECTED");
      } else {
        setBackendStatus(`FAILED: ${response.status}`);
      }
    } catch (error) {
      console.error("[Frontend] Request Error:", error);
      setBackendStatus(`OFFLINE`);
    }
    setLoading(false);
  };

  useEffect(() => {
    const canvas = document.getElementById("neural");
    if (canvas) initNeural(canvas);
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderList = (title, items) => (
    <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm flex flex-col h-full shadow-lg">
      <h3 className="text-neo-cyan font-bold tracking-widest mb-3 border-b border-neo-cyan/30 pb-2 uppercase text-xs flex justify-between">
        {title}
        <span className="animate-pulse text-[10px]">● LIVE</span>
      </h3>
      <div className="flex-1 overflow-y-auto max-h-48 text-sm text-neo-cyan/80 font-mono">
        {items && items.length > 0 ? (
          <ul className="space-y-2">
            {items.map((item, idx) => (
              <li key={idx} className="flex justify-between items-center border-b border-neo-cyan/10 pb-1">
                {typeof item === 'object' ? (
                  <>
                    <span className="text-neo-cyan truncate mr-2">{item.id}</span>
                    <span className="text-neo-amber font-bold">${item.balance.toFixed(2)}</span>
                  </>
                ) : (
                  <span className="flex items-center">
                    <span className="w-1.5 h-1.5 bg-neo-cyan rounded-full mr-2 shadow-sm shadow-neo-cyan" />
                    {item}
                  </span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div className="flex flex-col items-center justify-center h-20 opacity-50 italic text-xs">
            <p>Sincronizando...</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-start overflow-x-hidden bg-neo-bg py-10 text-neo-cyan font-sans">
      <canvas id="neural" className="fixed inset-0 z-0 opacity-40 pointer-events-none" />
      <div className="z-10 text-center space-y-8 p-4 w-full max-w-7xl">
        <header className="mb-10">
          <h1 className="text-5xl md:text-7xl font-black text-glow-cyan uppercase tracking-tighter drop-shadow-md inline-block">
            Omni-Revenue
          </h1>
          <div className="h-1 w-full bg-gradient-to-r from-transparent via-neo-cyan to-transparent mt-2" />
          <p className="text-neo-cyan/70 tracking-[0.5em] uppercase text-[10px] font-black mt-3 text-center w-full">
            Autonomous Business OS
          </p>
        </header>

        <div className="flex flex-col items-center justify-center space-y-4 pb-6">
          <NeoButton variant="cyan" onClick={fetchAllData} className="px-10 py-3 font-black tracking-tighter">
            {loading ? "PROCESSING..." : "FORCE SYNC"}
          </NeoButton>
          <div className="flex items-center space-x-4 text-[10px] font-black font-mono text-neo-cyan/60 uppercase tracking-widest bg-neo-cyan/5 px-4 py-1 rounded-full border border-neo-cyan/10">
            <span>Status: <span className={backendStatus === "CONNECTED" ? "text-neo-cyan" : "text-neo-magenta"}>{backendStatus}</span></span>
            <span className="opacity-30">|</span>
            <span>Clock: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full text-left">
          <NeoCard title="KERNEL STATUS" value={data.estado_sistema} status="ONLINE" variant="cyan" />
          <NeoCard title="TOTAL BALANCE" value={`$${data.balance.global.toFixed(2)}`} status="USDT" variant="amber" />
          <NeoCard title="OPPORTUNITIES" value={data.oportunidades_globales} status="LIST" variant="magenta" />
          <NeoCard title="GATEWAY" value={data.estado_gateway} status="STABLE" variant="cyan" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 w-full text-left">
          <div className="p-5 border border-neo-cyan/30 rounded bg-neo-bg/90 backdrop-blur-md flex flex-col shadow-lg shadow-neo-cyan/10">
             <h3 className="text-neo-cyan font-bold tracking-widest mb-5 border-b border-neo-cyan/30 pb-2 uppercase text-xs">
                Unit Monitoring (UAE)
             </h3>
             <div className="space-y-4">
               <div className="flex justify-between items-end border-b border-neo-cyan/10 pb-1">
                  <span className="text-neo-cyan/60 text-[10px] font-black uppercase">Active</span>
                  <span className="text-2xl font-black text-neo-cyan">{data.uaes.activas}</span>
               </div>
               <div className="flex justify-between items-end border-b border-neo-cyan/10 pb-1">
                  <span className="text-neo-cyan/60 text-[10px] font-black uppercase">Scaling</span>
                  <span className="text-2xl font-black text-neo-cyan">{data.uaes.duplicadas}</span>
               </div>
               <div className="flex justify-between items-end">
                  <span className="text-neo-cyan/60 text-[10px] font-black uppercase">Terminated</span>
                  <span className="text-2xl font-black text-neo-magenta">{data.uaes.muertas}</span>
               </div>
             </div>
          </div>
          {renderList("Core Agents", data.agentes_globales)}
          {renderList("Capital Distribution", data.balance.uaes)}
        </div>
      </div>
    </div>
  );
}

export default App;
