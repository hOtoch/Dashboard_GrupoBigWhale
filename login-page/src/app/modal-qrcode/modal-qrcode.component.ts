import { Component, Input,Output,EventEmitter } from '@angular/core';

@Component({
  selector: 'app-modal-qrcode',
  templateUrl: './modal-qrcode.component.html',
  styleUrls: ['./modal-qrcode.component.css']
})
export class ModalQrcodeComponent {
  @Input() qrCodeImage : string = '';
  @Output() closeModal: EventEmitter<void> = new EventEmitter<void>();
  @Output() openModalCode: EventEmitter<void> = new EventEmitter<void>();


  onCloseModal(): void {
    this.closeModal.emit();
  }

  openModalCodeEmit(): void {
    this.openModalCode.emit();
  }
}
