import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { LoginResponse } from './models/login-response.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:5000';  // URL da API Flask
  private tokenKey = 'token';  
  private userIdKey = 'userId';  

  constructor(private http: HttpClient) {}

  login(data: { email: string; senha: string }): Observable<LoginResponse> {
    const url = `${this.apiUrl}/login`;
    return this.http.post<LoginResponse>(url, data).pipe(
      tap((response: LoginResponse) => {
        localStorage.setItem(this.tokenKey, response.access_token);
      })
    );
  }

  loginWithGoogle(): string {
    return `${this.apiUrl}/login/google`;
  }

  verificaEmail(email: string): Observable<{ message: string }> {
    const url = `${this.apiUrl}/verify_email`;
    return this.http.post<{ message: string }>(url, { email });
  }

  forgotPassword(email: string): Observable<{ message: string }> {
    const url = `${this.apiUrl}/forgot-password`;
    return this.http.post<{ message: string }>(url, { email }).pipe(
      tap((response) => {
        console.log('Resposta do servidor:', response);
      }),
      catchError(this.handleError)  // Captura o erro
    );
  }

  resetPassword(token: string, newPassword: string): Observable<any> {
    const url = `${this.apiUrl}/reset-password/${token}`;  
    const body = { new_password: newPassword }; 

    return this.http.post(url, body);  
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }


  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userIdKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private handleError(error: HttpErrorResponse) {
    // Aqui você pode personalizar o erro de acordo com a resposta
    console.error('Ocorreu um erro:', error);
    return throwError(() => new Error('Erro ao realizar a requisição. Tente novamente.'));
  }
}
