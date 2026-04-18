import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

function App() {
  const [step, setStep] = useState(1);
  const [dbType, setDbType] = useState("");
  const [status, setStatus] = useState("");
  const [profiles, setProfiles] = useState<string[]>([]);
  const [selectedProfile, setSelectedProfile] = useState("");

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  useEffect(() => {
    if (step === 1) {
      loadProfiles();
    }
  }, [step]);

  async function loadProfiles() {
    try {
      const p = await invoke<string[]>("get_aws_profiles");
      setProfiles(p);
      if (p.length > 0) {
        setSelectedProfile(p[0]); // Selecciona el primero por defecto
      }
    } catch (error) {
      console.error("Error al cargar perfiles", error);
    }
  }

  async function checkAws() {
    if (!selectedProfile) {
      setStatus("Por favor, selecciona un perfil primero.");
      return;
    }
    
    setStatus("Verificando autenticación SSO...");
    // Acá verificaremos el login real luego
    setTimeout(() => {
      setStatus("¡Validación exitosa!");
      nextStep();
    }, 1500);
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center py-10 px-4 font-sans text-slate-800">
      <div className="w-full max-w-3xl bg-white shadow-2xl rounded-2xl overflow-hidden flex flex-col min-h-[550px] border border-slate-100">
        {/* Header - Corporate Branding */}
        <div className="bg-slate-900 px-8 py-5 flex items-center justify-between shadow-md">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded text-white flex items-center justify-center font-bold">W</div>
            <h1 className="text-white text-xl font-medium tracking-wide">WPOSS <span className="font-light text-slate-400">AWS Backup Manager</span></h1>
          </div>
          <div className="flex space-x-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className={`w-2.5 h-2.5 rounded-full ${step >= s ? 'bg-blue-500' : 'bg-slate-700'}`} />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-10 flex flex-col bg-white">
          {/* STEP 1: PERFILES */}
          {step === 1 && (
            <div className="flex-1 flex flex-col justify-center items-center text-center space-y-8 animate-fade-in">
              <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center shadow-inner border border-blue-100 text-blue-600">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                </svg>
              </div>
              <div>
                <h2 className="text-3xl font-semibold text-slate-800 tracking-tight">Conexión Segura AWS</h2>
                <p className="text-slate-500 mt-3 max-w-md mx-auto leading-relaxed">
                  Selecciona tu perfil corporativo SSO. Se requiere una sesión activa para listar y descargar los respaldos disponibles.
                </p>
              </div>

              <div className="w-full max-w-sm mt-4">
                <label className="block text-left text-sm font-medium text-slate-700 mb-2">Perfil AWS Detectado</label>
                <div className="relative">
                  <select 
                    value={selectedProfile}
                    onChange={(e) => setSelectedProfile(e.target.value)}
                    className="block w-full pl-4 pr-10 py-3 text-base border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm bg-slate-50 text-slate-800 appearance-none border"
                  >
                    {profiles.length > 0 ? (
                      profiles.map(p => <option key={p} value={p}>{p}</option>)
                    ) : (
                      <option value="">Cargando perfiles locales...</option>
                    )}
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <button
                onClick={checkAws}
                disabled={profiles.length === 0}
                className="mt-4 w-full max-w-sm bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-medium py-3.5 px-8 rounded-lg shadow transition-all duration-200"
              >
                Autenticar & Continuar
              </button>
              {status && <p className="text-sm font-medium text-blue-600 animate-pulse">{status}</p>}
            </div>
          )}

          {/* STEP 2: TIPO BACKUP */}
          {step === 2 && (
            <div className="flex-1 flex flex-col animate-fade-in">
              <div className="mb-8">
                <h2 className="text-2xl font-semibold text-slate-800">Seleccionar Motor de Datos</h2>
                <p className="text-slate-500 mt-1">Elige el formato del backup que deseas consultar en el bucket de S3 ({selectedProfile}).</p>
              </div>
              
              <div className="grid grid-cols-3 gap-5 flex-1 items-start">
                {[
                  { id: "sqlserver", title: "SQL Server", format: "BAK / TRN", icon: "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" },
                  { id: "postgres", title: "PostgreSQL", format: "SQL / DUMP", icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" },
                  { id: "compressed", title: "Comprimidos", format: "ZIP / TAR.GZ", icon: "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" }
                ].map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setDbType(item.id)}
                    className={`cursor-pointer rounded-xl border p-6 flex flex-col items-center justify-center transition-all duration-300 ${
                      dbType === item.id 
                      ? "border-blue-500 bg-blue-50 ring-2 ring-blue-100 transform scale-[1.02]" 
                      : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
                    }`}
                  >
                    <svg className={`w-12 h-12 mb-4 ${dbType === item.id ? 'text-blue-600' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.icon} />
                    </svg>
                    <h3 className="font-semibold text-slate-800 text-lg">{item.title}</h3>
                    <p className="text-xs font-semibold text-slate-400 mt-2 tracking-wide uppercase">{item.format}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 3: DESCARGA */}
          {step === 3 && (
            <div className="flex-1 flex flex-col justify-center items-center animate-fade-in max-w-lg mx-auto w-full text-center">
              <div className="w-16 h-16 mb-6 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </div>
              <h2 className="text-2xl font-semibold text-slate-800 mb-2">Preparando Descarga</h2>
              <p className="text-slate-500 mb-8">
                Consultando archivos de <span className="font-semibold text-slate-700">{dbType.toUpperCase()}</span> en la cuenta <span className="font-semibold text-slate-700">{selectedProfile}</span>...
              </p>
              
              <div className="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden border border-slate-200">
                <div className="bg-blue-500 h-2 rounded-full relative">
                  <div className="absolute top-0 left-0 bottom-0 right-0 overflow-hidden">
                    <div className="w-full h-full bg-blue-400 opacity-30 animate-pulse"></div>
                  </div>
                </div>
              </div>
              <div className="w-full flex justify-between text-xs font-medium text-slate-500">
                <span>Conectando con S3...</span>
                <span>Calculando tamaño...</span>
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="border-t border-slate-100 px-8 py-5 flex justify-between bg-slate-50 mt-auto">
          <button
            onClick={prevStep}
            disabled={step === 1}
            className={`font-medium py-2.5 px-6 rounded-md transition-colors text-sm ${
              step === 1 ? "text-slate-300 cursor-not-allowed opacity-0" : "text-slate-600 hover:bg-slate-200"
            }`}
          >
            ← Atrás
          </button>

          {step === 2 && (
            <button
              onClick={nextStep}
              disabled={!dbType}
              className={`font-medium py-2.5 px-8 rounded-md shadow-sm transition-all text-sm ${
                !dbType ? "bg-slate-200 text-slate-400 cursor-not-allowed" : "bg-slate-800 hover:bg-slate-900 text-white"
              }`}
            >
              Siguiente Paso →
            </button>
          )}
          
          {step === 3 && (
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-8 rounded-md shadow-sm transition-all text-sm">
              Cancelar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
