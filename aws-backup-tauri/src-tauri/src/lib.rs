use std::fs;
use std::path::PathBuf;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn get_aws_profiles() -> Vec<String> {
    let mut profiles = Vec::new();
    
    // Obtener el directorio home (USERPROFILE en Windows)
    let home_dir = match std::env::var("USERPROFILE").or_else(|_| std::env::var("HOME")) {
        Ok(dir) => PathBuf::from(dir),
        Err(_) => return profiles,
    };

    let config_path = home_dir.join(".aws").join("config");

    if !config_path.exists() {
        return profiles;
    }

    // Leer el archivo de configuraciÃ³n
    if let Ok(content) = fs::read_to_string(config_path) {
        for line in content.lines() {
            let line = line.trim();
            // Buscar lÃ­neas que definen un perfil como: [profile minombre] o [default]
            if line.starts_with('[') && line.ends_with(']') {
                let section = &line[1..line.len() - 1].trim();
                
                if section.starts_with("profile ") {
                    let profile_name = section.replace("profile ", "").trim().to_string();
                    profiles.push(profile_name);
                } else if section == &"default" {
                    profiles.push("default".to_string());
                }
            }
        }
    }

    profiles
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, get_aws_profiles])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
