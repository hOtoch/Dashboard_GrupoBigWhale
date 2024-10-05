import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { HttpClientModule } from '@angular/common/http';
import { EsqueciMinhaSenhaComponent } from './esqueci-minha-senha/esqueci-minha-senha.component';
import { ResetarSenhaComponent } from './resetar-senha/resetar-senha.component';
import { ModalQrcodeComponent } from './modal-qrcode/modal-qrcode.component';
import { ModalCodeComponent } from './modal-code/modal-code.component';


@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    EsqueciMinhaSenhaComponent,
    ResetarSenhaComponent,
    ModalQrcodeComponent,
    ModalCodeComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
