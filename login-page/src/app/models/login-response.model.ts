export interface LoginResponse {
    access_token: string;
}

export interface AuthenticatorResponse {
    secret: string;
    qr_code: string;
}