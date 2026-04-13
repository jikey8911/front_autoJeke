import { useEffect } from 'react';
import { initNeural, NeoCard } from '@tu-usuario/jeikei-ui';

function App() {
  useEffect(() => {
    const canvas = document.getElementById("neural");
    if (canvas) {
      initNeural(canvas);
    }
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-neo-bg">
      {/* Fondo de Red Neuronal */}
      <canvas id="neural" className="absolute inset-0 z-0 opacity-40" />
      
      <div className="z-10 text-center space-y-8 p-4">
        <h1 className="text-5xl md:text-7xl font-bold text-glow-cyan uppercase tracking-widest text-neo-cyan drop-shadow-md">
          AutomataJeiKei
        </h1>
        <p className="text-neo-cyan/70 tracking-widest uppercase text-sm font-bold">
          Sistema Operativo Autónomo de Negocios
        </p>
        
        {/* Componente de demostración del HUD Kit */}
        <div className="max-w-md mx-auto pt-8">
          <NeoCard 
            title="CORE SYSTEM" 
            value="ONLINE" 
            status="INITIALIZING NEURAL NET..." 
            variant="cyan" 
          />
        </div>
      </div>
    </div>
  );
}

export default App;