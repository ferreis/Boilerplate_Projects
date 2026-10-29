use std::{convert::Infallible, env, net::SocketAddr};

use http_body_util::Full;
use hyper::{
    body::{Bytes, Incoming},
    header::{CONTENT_TYPE, HeaderValue},
    server::conn::http1,
    service::service_fn,
    Method, Request, Response, StatusCode,
};
use hyper_util::rt::TokioIo;
use tokio::net::TcpListener;

async fn handle(request: Request<Incoming>) -> Result<Response<Full<Bytes>>, Infallible> {
    let (status, body) = match (request.method(), request.uri().path()) {
        (&Method::GET, "/health") => (StatusCode::OK, r#"{"status":"ok"}"#),
        _ => (StatusCode::NOT_FOUND, r#"{"error":"not_found"}"#),
    };

    let mut response = Response::new(Full::new(Bytes::from(body)));
    *response.status_mut() = status;
    response.headers_mut().insert(
        CONTENT_TYPE,
        HeaderValue::from_static("application/json; charset=utf-8"),
    );
    Ok(response)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let port: u16 = env::var("BACKEND_PORT")
        .unwrap_or_else(|_| "8000".to_owned())
        .parse()?;
    let address = SocketAddr::from(([0, 0, 0, 0], port));
    let listener = TcpListener::bind(address).await?;
    println!("Rust/Hyper escutando em {address}");

    loop {
        let (stream, _) = listener.accept().await?;
        tokio::spawn(async move {
            let io = TokioIo::new(stream);
            if let Err(error) = http1::Builder::new()
                .serve_connection(io, service_fn(handle))
                .await
            {
                eprintln!("Erro na conexão HTTP: {error}");
            }
        });
    }
}
