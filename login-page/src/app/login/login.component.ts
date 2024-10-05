import { Component,OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { LoginResponse } from '../models/login-response.model';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements  AfterViewInit{
  email: string = '';
  password: string = '';
  errorMessage: string = '';
  isModalQrCodeOpen: boolean = false;
  isModalCodeOpen: boolean = false;
  qrCodeBase64: string = '';
  token : string = '';


  constructor(private authService: AuthService, private router: Router) { }

  @ViewChild('videoBackground', { static: false }) videoRef?: ElementRef<HTMLVideoElement>;


  ngAfterViewInit(): void {

    document.body.addEventListener('click', () => {
      this.playVideo();
    }, { once: true }); // Adiciona o evento apenas uma vez
  }


  playVideo(): void {
    if (this.videoRef) {
      const video = this.videoRef.nativeElement;
      video.currentTime = 0; // Reinicia o vídeo do início
      video.muted = true; // Garante que o vídeo esteja sem som
      video.play().catch(error => {
        console.error('Erro ao tentar reproduzir o vídeo:', error);
      });
    }
  }

  login() {
    const loginData = {
      email: this.email,
      senha: this.password
    };

    this.authService.login(loginData).subscribe(
      (response: LoginResponse) => {  
        this.token = this.authService.getToken() ?? '';  // Obtém o token do login
        this.errorMessage = '';

        const authenticator_response = this.authService.setupAuthenticator(loginData.email).subscribe(
          (response) => {
            if (!response.qr_code) {
              // Usuário já configurou o Authenticator
              this.email = loginData.email;
              this.isModalCodeOpen = true;
            }else{
              this.qrCodeBase64 = `data:image/png;base64,${response.qr_code}`;
              this.isModalQrCodeOpen = true;
            }
            
          },
          (error) => {
            console.log('Erro ao configurar o Authenticator:', error);
          }
        );

      },
      (error) => {
        this.errorMessage = 'Dados de login inválidos';
      }
    );
  }

  closeQrCodeModal(): void {
    this.isModalQrCodeOpen = false;
  }

  closeCodeModal(): void {
    this.isModalCodeOpen = false;
  }

  openModalCode(): void {
    this.isModalQrCodeOpen = false;
    this.isModalCodeOpen = true;
  }

}
