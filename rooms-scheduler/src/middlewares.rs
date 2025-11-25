
use axum_responses::http::HttpResponse;
use axum::{
    http::header,
    middleware::Next,
    response::Response,
    extract::Request
};

use crate::jwt::verify_token;

pub async fn require_access_token(mut req: Request, next: Next) -> Result<Response, HttpResponse> {
    let token_encoded = req
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|value| value.to_str().ok())
        .and_then(extract_bearer_token);

    let token = match token_encoded {
            Some(token) => token,
            None => return Err(HttpResponse::Unauthorized()),
        };

    let claims = match verify_token(token) {
            Ok(claims) => claims,
            Err(_) => return Err(HttpResponse::Unauthorized()),
        };

    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}

pub async fn require_administrator_role(req: Request, next: Next) -> Result<Response, HttpResponse> {
    let claims = req
        .extensions()
        .get::<crate::models::Claims>()
        .ok_or(HttpResponse::Unauthorized())?;

    if !claims.rol.eq_ignore_ascii_case("administrator") {
        return Err(HttpResponse::Unauthorized());
    }

    Ok(next.run(req).await)
}

fn extract_bearer_token(header_value: &str) -> Option<&str> {
    header_value
        .split_once(' ')
        .filter(|(scheme, _)| scheme.eq_ignore_ascii_case("Bearer"))
        .map(|(_, token)| token.trim())
        .filter(|token| !token.is_empty())
}
