import { useEffect, useState } from 'react';
import { initNeural, NeoCard, NeoButton } from '@jikey8911/jeikei-ui';

function App() {
  const [data, setData] = useState({
    agents: null,
    opportunities: null,
    running_tasks: null,
    balance: null,
    status: null,
    mitosis: null,
    kill: null,
    test_ws: null
  });
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("CHECKING...");

  const testBackendConnection = async () => {
    const apiUrl = '/api';
    try {
      console.log(`[Frontend] Pidiendo test_ws a: ${apiUrl}/test_ws`);
      const response = await fetch(`${apiUrl}/test_ws`);
      const jsonResponse = await response.json();
      console.log(`[Frontend] Respuesta de test_ws:`, jsonResponse);
      
      // La API nativa devuelve un array de modelos o un objeto con info
      if (response.ok) {
        setBackendStatus("CONNECTED");
        return jsonResponse;
      } else {
        setBackendStatus(`FAILED: ${response.status}`);
        return null;
      }
    } catch (error) {
      console.error("[Frontend] Error en testBackendConnection:", error);
      setBackendStatus(`FAILED: ${error.message}`);
      return null;
    }
  };

  const fetchData = async () => {
    setLoading(true);
    const apiUrl = '/api';
    
    // Lista de endpoints compatibles con la nueva API Nativa v1
    const endpoints = ['agents', 'status', 'test_ws'];
    
    const results = { ...data };
    for (const endpoint of endpoints) {
      try {
        console.log(`[Frontend] Consultando Backend -> API Nativa: ${apiUrl}/${endpoint}`);
        const response = await fetch(`${apiUrl}/${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        results[endpoint] = await response.json();
      } catch (error) {
        console.error(`[Frontend] Fallo en ${endpoint}:`, error);
        results[endpoint] = { error: "Fallo de conexión", details: error.message };
      }
    }
    setData(results);
    setLoading(false);
  };

  useEffect(() => {
    const canvas = document.getElementById("neural");
    if (canvas) initNeural(canvas);
    
    const init = async () => {
      await testBackendConnection();
      await fetchData();
    };
    init();
  }, []);

  const renderRawData = (title, json) => (
    <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm flex flex-col h-full">
      <h3 className="text-neo-cyan font-bold tracking-widest mb-2 border-b border-neo-cyan/30 pb-2 uppercase text-xs">
        {title}
      </h3>
      <div className="flex-1 overflow-y-auto max-h-40 text-[10px] text-neo-cyan/80 font-mono whitespace-pre-wrap">
        {loading ? <span className="animate-pulse">Syncing...</span> : JSON.stringify(json, null, 2)}
      </div>
    </div>
  );

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-start overflow-x-hidden bg-neo-bg py-10 text-neo-cyan">
      <canvas id="neural" className="fixed inset-0 z-0 opacity-40 pointer-events-none" />

      <div className="z-10 text-center space-y-8 p-4 w-full max-w-7xl">
        <h1 className="text-5xl md:text-7xl font-bold text-glow-cyan uppercase tracking-widest drop-shadow-md">
          AutomataJeiKei
        </h1>
        <p className="text-neo-cyan/70 tracking-widest uppercase text-sm font-bold">
          Sistema Operativo Autónomo de Negocios
        </p>

        <div className="flex flex-col items-center justify-center space-y-4 pb-4">
          <NeoButton variant="cyan" onClick={fetchData}>
            {loading ? "SYNCING..." : "FORCE SYNC DATA"}
          </NeoButton>
          <div className="text-xs font-mono text-neo-cyan/60 uppercase">
            Backend API Link: <span className={backendStatus === "CONNECTED" ? "text-neo-cyan" : "text-neo-magenta"}>{backendStatus}</span>
          </div>
        </div>

        {/* Top Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          <NeoCard title="API NATIVA V1" value={backendStatus === "CONNECTED" ? "READY" : "OFFLINE"} status="CORE PORT 10424" variant="cyan" />
          <NeoCard title="ACTIVE AGENTS" value={loading ? "..." : (data.agents?.length || "0")} status="SYSTEM MAPPING" variant="amber" />
          <NeoCard title="MODELS DETECTED" value={loading ? "..." : (data.test_ws?.models?.length || "SYNC")} status="GATEWAY TELEMETRY" variant="magenta" />
        </div>

        {/* Detailed Data Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6 w-full text-left">
          {renderRawData("Agents List", data.agents)}
          {renderRawData("Gateway Status", data.status)}
          {renderRawData("Models / Health", data.test_ws)}
        </div>
      </div>
    </div>
  );
}

export default App;