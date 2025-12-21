use std::process::{Command, Child};
use std::sync::{Arc, Mutex};
use std::net::TcpListener;
use tauri::Manager;

struct AppState {
    python_process: Arc<Mutex<Option<Child>>>,
    server_port: Arc<Mutex<u16>>,
}

impl AppState {
    fn cleanup_server(&self) {
        let mut lock = self.python_process.lock().unwrap();
        if let Some(mut process) = lock.take() {
            let pid = process.id();
            log::info!("Cleanup: Stopping server (PID: {})...", pid);

            // Kill child processes first
            #[cfg(unix)]
            {
                let _ = std::process::Command::new("pkill")
                    .arg("-P")
                    .arg(pid.to_string())
                    .output();
                std::thread::sleep(std::time::Duration::from_millis(200));
            }

            // Kill main process
            let _ = process.kill();
            let _ = process.wait();
            log::info!("Cleanup: Server stopped");
        }
    }
}

impl Drop for AppState {
    fn drop(&mut self) {
        log::info!("AppState dropping - cleaning up server");
        self.cleanup_server();
    }
}

fn find_available_port() -> Result<u16, std::io::Error> {
    // Try to find an available port in the range 5555-5655 (100 ports)
    // This keeps ports predictable and avoids conflicts with other services
    const START_PORT: u16 = 5555;
    const END_PORT: u16 = 5655;

    for port in START_PORT..=END_PORT {
        match TcpListener::bind(("127.0.0.1", port)) {
            Ok(listener) => {
                // Port is available, drop the listener to free it
                drop(listener);
                log::info!("Found available port: {}", port);
                return Ok(port);
            }
            Err(_) => {
                // Port is in use, try next one
                continue;
            }
        }
    }

    // If all ports in range are taken, return error
    Err(std::io::Error::new(
        std::io::ErrorKind::AddrInUse,
        format!("No available ports found in range {}-{}", START_PORT, END_PORT)
    ))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  let app_state = AppState {
      python_process: Arc::new(Mutex::new(None)),
      server_port: Arc::new(Mutex::new(5555)), // Default, will be updated if we spawn server
  };

  // Register signal handlers for cleanup
  let cleanup_state = app_state.python_process.clone();
  ctrlc::set_handler(move || {
      log::info!("Received interrupt signal - cleaning up server...");
      let mut lock = cleanup_state.lock().unwrap();
      if let Some(mut process) = lock.take() {
          let _ = process.kill();
          let _ = process.wait();
      }
      std::process::exit(0);
  }).expect("Error setting Ctrl-C handler");

  tauri::Builder::default()
    .manage(app_state)
    .setup(|app| {
      // Enable logging for both debug and release modes
      // In release mode, logs are saved to:
      // - macOS: ~/Library/Logs/BrowserAutomation/
      // - Linux: ~/.local/share/BrowserAutomation/logs/
      // - Windows: %APPDATA%\BrowserAutomation\logs\
      let log_plugin = if cfg!(debug_assertions) {
        // Debug mode: log to stdout
        tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
      } else {
        // Release mode: log to file
        tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .target(tauri_plugin_log::Target::new(
                tauri_plugin_log::TargetKind::LogDir { file_name: None }
            ))
      };

      app.handle().plugin(log_plugin.build())?;

      log::info!("Application starting...");
      log::info!("Version: {}", env!("CARGO_PKG_VERSION"));

      // Spawn Python Flask server (production mode only)
      if !cfg!(debug_assertions) {
          log::info!("Starting Python Flask server...");

          // Find an available port
          let port = match find_available_port() {
              Ok(p) => {
                  log::info!("Found available port: {}", p);
                  p
              },
              Err(e) => {
                  log::error!("Failed to find available port: {}", e);
                  return Err(Box::new(e).into());
              }
          };

          // Store the port in app state
          *app.state::<AppState>().server_port.lock().unwrap() = port;

          // Production mode - Python and dependencies are bundled with the app
          let resource_dir = match app.path().resource_dir() {
              Ok(dir) => dir,
              Err(e) => {
                  log::error!("Failed to get resource dir: {}", e);
                  return Err(Box::new(e).into());
              }
          };

          // Resources specified in tauri.conf.json with ../ paths are placed in _up_ subdirectory
          let resource_base = resource_dir.join("_up_");
          let server_binary = resource_base.join("bundle-bin").join("server");

          log::info!("Resource dir: {:?}", resource_dir);
          log::info!("Server binary: {:?}", server_binary);

          // Check if binary exists before trying to spawn
          if !server_binary.exists() {
              log::error!("Server binary not found at: {:?}", server_binary);
              return Err("Server binary not found in bundle".into());
          }

          log::info!("Server binary found, starting server on port {}...", port);

          // Check for VERBOSE environment variable to pass to server
          let verbose_flag = std::env::var("VERBOSE")
              .map(|v| v.to_lowercase() == "true" || v == "1")
              .unwrap_or(false);

          // Start server binary in its own process group so we can kill it and all children
          let mut cmd = Command::new(&server_binary);

          // On Unix, create a new process group for the server
          #[cfg(unix)]
          {
              use std::os::unix::process::CommandExt;
              cmd.process_group(0);
          }

          // Add port argument
          cmd.arg("--port").arg(port.to_string());

          // Add verbose flag if set
          if verbose_flag {
              log::info!("VERBOSE mode enabled - passing --verbose to server");
              cmd.arg("--verbose");
          }

          log::info!("Spawning server process...");
          let server_child = match cmd.spawn() {
                  Ok(child) => {
                      log::info!("Server process started successfully (PID: {})", child.id());
                      child
                  },
                  Err(e) => {
                      log::error!("Failed to start server: {}", e);
                      return Err(Box::new(e).into());
                  }
              };

          // Store the process handle
          *app.state::<AppState>().python_process.lock().unwrap() = Some(server_child);

          log::info!("Flask server starting on port {}...", port);

          // Wait for server to be ready, then navigate the window to it
          let window = app.get_webview_window("main").expect("Failed to get main window");
          let server_url = format!("http://127.0.0.1:{}", port);
          std::thread::spawn(move || {
              // Wait for server to start (up to 10 seconds)
              for attempt in 1..=20 {
                  std::thread::sleep(std::time::Duration::from_millis(500));

                  // Check if server is responding
                  let check_url = server_url.clone();
                  if let Ok(response) = ureq::get(&check_url).timeout(std::time::Duration::from_millis(500)).call() {
                      if response.status() == 200 {
                          log::info!("Flask server is ready after {} attempts", attempt);
                          // Navigate to the Flask server
                          let nav_script = format!("window.location.href = '{}'", server_url);
                          if let Err(e) = window.eval(&nav_script) {
                              log::error!("Failed to navigate window: {}", e);
                          }
                          return;
                      }
                  }
              }
              log::warn!("Flask server did not become ready within 10 seconds");
          });
      } else {
          log::info!("Development mode: Flask server should be started manually with 'npm run server'");
      }

      log::info!("Setup complete!");
      Ok(())
    })
    .on_window_event(|window, event| {
      // Clean up server process when window closes
      match event {
          tauri::WindowEvent::CloseRequested { .. } => {
              log::info!("Window close requested - cleaning up server...");
              let app_state: tauri::State<AppState> = window.state();
              app_state.cleanup_server();
              // Explicitly close the window to complete the close operation
              let _ = window.close();
          }
          tauri::WindowEvent::Destroyed => {
              log::info!("Window destroyed");
          }
          _ => {}
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
