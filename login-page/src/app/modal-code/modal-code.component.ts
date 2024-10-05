import { Component, Output,Input,EventEmitter } from '@angular/core';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-modal-code',
  templateUrl: './modal-code.component.html',
  styleUrls: ['./modal-code.component.css']
})



export class ModalCodeComponent {
  @Output() closeModal: EventEmitter<void> = new EventEmitter<void>();
  @Input() email: string = '';
  @Input() token: string = '';
  authenticatorCode: string = '';
  verificationMessage: string = '';


  constructor(private authService: AuthService) { }

  onCloseModal(): void {
    this.closeModal.emit();
  }

  verifyAuthenticatorCode(): void {
    this.authService.verifyAuthenticator(this.email,this.authenticatorCode).subscribe(
      (response) => {
        window.location.href = `http://localhost:8501?token=${this.token}`;
      },
      (error) => {
        this.verificationMessage = "Código inserido inválido"
      }
      
    );
  }

}
