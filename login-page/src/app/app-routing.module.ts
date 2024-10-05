import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { EsqueciMinhaSenhaComponent } from './esqueci-minha-senha/esqueci-minha-senha.component';
import { ResetarSenhaComponent } from './resetar-senha/resetar-senha.component';
import { ModalQrcodeComponent } from './modal-qrcode/modal-qrcode.component';

const routes: Routes = [
{path: 'login', component: LoginComponent},
{path: 'esqueci-minha-senha', component: EsqueciMinhaSenhaComponent},
{path: 'resetar-senha/:token', component: ResetarSenhaComponent},
{path: 'authenticator', component: ModalQrcodeComponent},
{path: '', redirectTo: '/login', pathMatch: 'full'}
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
