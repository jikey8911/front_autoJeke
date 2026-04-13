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
    kill: null
  });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    const apiUrl = import.meta.env.VITE_API_URL || 'http://automata_backend:5000';
    const endpoints = ['agents', 'opportunities', 'running_tasks', 'balance', 'status', 'mitosis', 'kill'];
    
    const results = {};
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${apiUrl}/${endpoint}`);
        results[endpoint] = await response.json();
      } catch (error) {
        results[endpoint] = { error: "Connection Failed" };
      }
    }
    setData(results);
    setLoading(false);
  };

  useEffect(() => {
    const canvas = document.getElementById("neural");
    if (canvas) initNeural(canvas);
    fetchData();
  }, []);

  const renderRawData = (title, json) => (
    <div className="p-4 border border-neo-cyan/30 rounded bg-neo-bg/80 backdrop-blur-sm flex flex-col h-full">
      <h3 className="text-neo-cyan font-bold tracking-widest mb-2 border-b border-neo-cyan/30 pb-2 uppercase">
        {title}
      </h3>
      <div className="flex-1 overflow-y-auto max-h-40 text-xs text-neo-cyan/80 font-mono whitespace-pre-wrap">
        {loading ? <span className="animate-pulse">Fetching...</span> : JSON.stringify(json, null, 2)}
      </div>
    </div>
  );

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-start overflow-x-hidden bg-neo-bg py-10">
      <canvas id="neural" className="fixed inset-0 z-0 opacity-40 pointer-events-none" />

      <div className="z-10 text-center space-y-8 p-4 w-full max-w-7xl">
        <h1 className="text-5xl md:text-7xl font-bold text-glow-cyan uppercase tracking-widest text-neo-cyan drop-shadow-md">
          AutomataJeiKei
        </h1>
        <p className="text-neo-cyan/70 tracking-widest uppercase text-sm font-bold">
          Sistema Operativo Autónomo de Negocios
        </p>

        <div className="flex justify-center pb-4">
          <NeoButton variant="cyan" onClick={fetchData}>
            {loading ? "SYNCING..." : "FORCE SYNC DATA"}
          </NeoButton>
        </div>

        {/* Top Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          <NeoCard title="SYSTEM LINK" value={loading ? "SYNC..." : "ONLINE"} status="GATEWAY CONNECTION" variant="cyan" />
          <NeoCard title="GLOBAL BALANCE" value={loading ? "..." : (data.balance?.error ? "ERR" : "ACTIVE")} status="BROKER TELEMETRY" variant="amber" />
          <NeoCard title="MITOSIS / KILL" value={loading ? "..." : "TRACKING"} status="LIFECYCLE OPS" variant="magenta" />
        </div>

        {/* Detailed Data Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-6 w-full text-left">
          {renderRawData("Global Status", data.status)}
          {renderRawData("Active Agents", data.agents)}
          {renderRawData("Opportunities", data.opportunities)}
          {renderRawData("Running Tasks", data.running_tasks)}
          {renderRawData("Broker Balance", data.balance)}
          {renderRawData("Mitosis Events", data.mitosis)}
        </div>
      </div>
    </div>
  );
}

export default App;