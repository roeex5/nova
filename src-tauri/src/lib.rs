use std::process::{Command, Child};
use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    python_process: Mutex<Option<Child>>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  let app_state = AppState {
      python_process: Mutex::new(None),
  };

  tauri::Builder::default()
    .manage(app_state)
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // Spawn Python Flask server (production mode only)
      if !cfg!(debug_assertions) {
          println!("Starting Python Flask server...");

          // Production mode - Python and dependencies are bundled with the app
          let resource_dir = match app.path().resource_dir() {
              Ok(dir) => dir,
              Err(e) => {
                  eprintln!("ERROR: Failed to get resource dir: {}", e);
                  return Err(Box::new(e).into());
              }
          };

          // Resources are in the _up_ subdirectory due to ../ paths in tauri.conf.json
          let bundle_root = resource_dir.join("_up_");
          let server_script = bundle_root.join("server.py");
          let python_exe = bundle_root.join("bundle-venv").join("bin").join("python3");

          println!("Resource dir: {:?}", resource_dir);
          println!("Python interpreter: {:?}", python_exe);
          println!("Server script: {:?}", server_script);

          // Check if files exist before trying to spawn
          if !python_exe.exists() {
              eprintln!("ERROR: Python interpreter not found at: {:?}", python_exe);
              return Err("Python interpreter not found in bundle".into());
          }
          if !server_script.exists() {
              eprintln!("ERROR: Server script not found at: {:?}", server_script);
              return Err("Server script not found in bundle".into());
          }

          // Start Python server with bundled interpreter
          let python_child = match Command::new(&python_exe)
              .arg(&server_script)
              .spawn() {
                  Ok(child) => child,
                  Err(e) => {
                      eprintln!("ERROR: Failed to start Python server: {}", e);
                      return Err(Box::new(e).into());
                  }
              };

          // Store the process handle
          *app.state::<AppState>().python_process.lock().unwrap() = Some(python_child);

          // Note: The HTML placeholder will automatically redirect to localhost:5000
          // after checking that the Flask server is ready
          println!("Flask server starting... (HTML will auto-redirect when ready)");
      } else {
          println!("Development mode: Flask server should be started manually with 'npm run server'");
      }

      Ok(())
    })
    .on_window_event(|window, event| {
      // Clean up Python process when window closes
      if let tauri::WindowEvent::Destroyed = event {
          let app_state: tauri::State<AppState> = window.state();
          let mut lock = app_state.python_process.lock().unwrap();
          if let Some(mut process) = lock.take() {
              println!("Stopping Python server...");
              let _result = process.kill();
          }
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
