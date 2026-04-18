import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import "./App.css";

function App() {
  const [step, setStep] = useState(1);
  const [dbType, setDbType] = useState("");
  const [status, setStatus] = useState("");

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  async function checkAws() {
    setStatus("Verificando perfiles de AWS...");
    // Simularemos el llamado al backend en Rust
    setTimeout(() => {
      setStatus("¡Validación exitosa!");
      nextStep();
    }, 1500);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-6 text-gray-800">
      <div className="w-full max-w-2xl bg-white shadow-xl rounded-2xl overflow-hidden flex flex-col h-[500px]">
        {/* Header */}
        <div className="bg-blue-600 px-6 py-4 flex items-center justify-between">
          <h1 className="text-white text-xl font-bold tracking-wide">AWS Backup Manager</h1>
          <span className="text-blue-200 text-sm font-medium">Paso {step} de 3</span>
        </div>

        {/* Content */}
        <div className="flex-1 p-8 flex flex-col">
          {step === 1 && (
            <div className="flex-1 flex flex-col justify-center items-center text-center space-y-6">
              <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-3xl shadow-sm">
                ☁️
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-800">Bienvenido al Descargador de Backups</h2>
                <p className="text-gray-500 mt-2">
                  Esta herramienta te permite descargar backups de la nube S3 directamente con tu cuenta SSO corporativa.
                </p>
              </div>
              <button
                onClick={checkAws}
                className="mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg shadow-md transition-all duration-200"
              >
                Autenticar con AWS SSO
              </button>
              {status && <p className="text-blue-600 animate-pulse font-medium">{status}</p>}
            </div>
          )}

          {step === 2 && (
            <div className="flex-1 flex flex-col">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Selecciona el tipo de Backup</h2>
              <div className="grid grid-cols-2 gap-4 flex-1">
                {[
                  { id: "sqlserver", title: "SQL Server", icon: "🗄️", desc: ".bak, .trn, .dif" },
                  { id: "postgres", title: "PostgreSQL", icon: "🐘", desc: ".sql, .dump" },
                  { id: "compressed", title: "Comprimidos", icon: "📦", desc: ".zip, .rar, .7z" }
                ].map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setDbType(item.id)}
                    className={`cursor-pointer rounded-xl border-2 p-4 flex flex-col items-center justify-center transition-all ${
                      dbType === item.id 
                      ? "border-blue-600 bg-blue-50 shadow-md transform scale-105" 
                      : "border-gray-200 hover:border-blue-400 hover:bg-gray-50"
                    }`}
                  >
                    <span className="text-4xl mb-2">{item.icon}</span>
                    <h3 className="font-bold text-gray-800">{item.title}</h3>
                    <p className="text-xs text-gray-500 mt-1 text-center">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="flex-1 flex flex-col justify-center items-center">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Listo para Descargar</h2>
              <p className="text-gray-600 mb-8 border border-gray-200 bg-gray-50 px-4 py-2 rounded">
                Base de datos seleccionada: <strong>{dbType.toUpperCase()}</strong>
              </p>
              
              <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                <div className="bg-blue-600 h-4 rounded-full" style={{ width: "45%" }}></div>
              </div>
              <p className="text-sm font-medium text-gray-500">Descargando... 45%</p>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="border-t border-gray-100 px-6 py-4 flex justify-between bg-gray-50">
          <button
            onClick={prevStep}
            disabled={step === 1}
            className={`font-medium py-2 px-6 rounded-lg transition-colors ${
              step === 1 ? "text-gray-400 cursor-not-allowed" : "text-gray-600 hover:bg-gray-200"
            }`}
          >
            ← Volver
          </button>

          {step === 2 && (
            <button
              onClick={nextStep}
              disabled={!dbType}
              className={`font-semibold py-2 px-6 rounded-lg shadow-sm transition-all ${
                !dbType ? "bg-gray-300 text-gray-500 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            >
              Siguiente Paso →
            </button>
          )}
          
          {step === 3 && (
            <button className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg shadow-sm transition-all">
              Terminar y Cerrar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
