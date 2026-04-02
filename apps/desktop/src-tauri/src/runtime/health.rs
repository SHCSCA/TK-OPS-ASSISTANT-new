use std::net::{TcpStream, ToSocketAddrs};
use std::thread::sleep;
use std::time::Duration;

const DEFAULT_LOCAL_RUNTIME_HOST: &str = "127.0.0.1";

fn endpoint_host_port(endpoint: &str) -> Option<(String, u16)> {
    let raw = endpoint
        .trim()
        .strip_prefix("http://")
        .or_else(|| endpoint.trim().strip_prefix("https://"))
        .unwrap_or(endpoint.trim());
    let authority = raw.split('/').next()?.trim();
    let (host, port_text) = authority.rsplit_once(':')?;
    let port = port_text.parse::<u16>().ok()?;
    let normalized_host = if host.trim().is_empty() {
        DEFAULT_LOCAL_RUNTIME_HOST.to_string()
    } else {
        host.to_string()
    };
    Some((normalized_host, port))
}

pub fn probe_runtime_endpoint(endpoint: &str) -> bool {
    let Some((host, port)) = endpoint_host_port(endpoint) else {
        return false;
    };

    let address = format!("{host}:{port}");
    let Ok(mut socket_addresses) = address.to_socket_addrs() else {
        return false;
    };
    let Some(socket_address) = socket_addresses.next() else {
        return false;
    };

    TcpStream::connect_timeout(&socket_address, Duration::from_millis(500)).is_ok()
}

pub fn wait_for_runtime_ready(
    endpoint: &str,
    attempts: u32,
    interval: Duration,
) -> bool {
    for _ in 0..attempts {
        if probe_runtime_endpoint(endpoint) {
            return true;
        }
        sleep(interval);
    }
    false
}
