use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};

use crate::{config, models::Claims};

#[derive(Debug)]
pub enum JwtVerificationError {
    UnsupportedAlgorithm(String),
    InvalidTokenType,
    MissingClaims,
    InvalidToken(jsonwebtoken::errors::Error),
}

impl From<jsonwebtoken::errors::Error> for JwtVerificationError {
    fn from(err: jsonwebtoken::errors::Error) -> Self {
        JwtVerificationError::InvalidToken(err)
    }
}

pub fn verify_token(token: &str) -> Result<Claims, JwtVerificationError> {
    let config = config::load_env();

    let algorithm = match config.jwt_algorithm {
        "HS256" => Algorithm::HS256,
        "HS384" => Algorithm::HS384,
        "HS512" => Algorithm::HS512,
        other => return Err(JwtVerificationError::UnsupportedAlgorithm(other.to_string())),
    };

    let mut validation = Validation::new(algorithm);
    validation.validate_exp = true;

    let decoding_key = DecodingKey::from_secret(config.jwt_secret.as_bytes());
    let claims = decode::<Claims>(token, &decoding_key, &validation)
        .map_err(JwtVerificationError::from)?
        .claims;

    if claims.token_type != "access" {
        return Err(JwtVerificationError::InvalidTokenType);
    }

    if claims.sub.is_empty() || claims.rol.is_empty() || claims.user_id <= 0 {
        return Err(JwtVerificationError::MissingClaims);
    }

    Ok(claims)
}
