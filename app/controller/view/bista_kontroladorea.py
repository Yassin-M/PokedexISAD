from flask import render_template, request, redirect, url_for, flash, session
from app.controller.model.eredu_kontroladorea import EreduKontroladorea
import json


class BistaKontroladorea:
   def __init__(self):
      self.eredu_kontroladorea = EreduKontroladorea()
   
   def saioHasi(self, erabiltzailea, pasahitza):
      """Saioa hasteko orria"""
      if request.method == 'POST':
        
         if not erabiltzailea or not pasahitza:
            error = 'Mesedez, bete eremu guztiak'
            return render_template('login.html', error=error)
         
         erantzuna_json = self.eredu_kontroladorea.saioHasi(erabiltzailea, pasahitza)
         erantzuna = json.loads(erantzuna_json or '{}')
         ondo = erantzuna.get('ondo')
         erabiltzaile_izena = erantzuna.get('erabiltzaile_izena')
         rola = erantzuna.get('rola')
         mezua = erantzuna.get('mezua')
         
         if ondo:
            session['user'] = erabiltzaile_izena
            session['role'] = rola or 'usuario'
            if (rola or '').lower() == 'admin':
               return redirect('menu_admin.html')
            return redirect('menu.html')
         else:
            error = mezua
            return render_template('login.html', error=error)
      
      return render_template('login.html')
   
   def erregistratu(self):
      """Erregistro orria"""
      if request.method == 'POST':
         erabiltzailea = request.form.get('erabiltzailea')
         email = request.form.get('email')
         jaiotze_data = request.form.get('jaiotze_data')
         pasahitza = request.form.get('pasahitza')
         pasahitza2 = request.form.get('pasahitza_berretsi')
         
         error = None
         
         if not all([erabiltzailea, email, jaiotze_data, pasahitza, pasahitza2]):
            error = 'Mesedez, bete eremu guztiak'
         
         if error:
            return render_template('register.html', error=error)
         
         ondo, mensaje = self.eredu_kontroladorea.erregistratu(
            erabiltzailea, email, jaiotze_data, pasahitza, pasahitza2
         )
         
         if ondo:
            success = mensaje + ' Saioa hasi dezakezu orain.'
            return render_template('register.html', success=success)
         else:
            error = mensaje
            return render_template('register.html', error=error)
      
      return render_template('register.html')
   
   def datuakAldatu(self, user_id=None):
      """Profila editatzeko orria"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      if user_id:
         if session.get('role', '').lower() != 'admin':
            flash('Ez duzu baimenik orri hau ikusteko', 'error')
            return redirect(url_for('menu'))
         
         erabiltzaile_izena = user_id
         home_endpoint = 'kudeatu'
      else:
         erabiltzaile_izena = session['user']
         home_endpoint = 'menu_admin' if (session['role'].lower() == 'admin') else 'menu'
      
      query = "SELECT izena, pasahitza, rola, email, jaiotze_data FROM Erabiltzailea WHERE izena = ?"
      emaitza_lista = self.eredu_kontroladorea.db.select(query, (erabiltzaile_izena,))
      emaitza = emaitza_lista[0] if emaitza_lista else None
      
      if request.method == 'POST':
         izena = request.form['izena'].strip() if request.form['izena'].strip() else None
         email = request.form['email'].strip() if request.form['email'].strip() else None
         jaiotze_data = request.form['jaiotza'].strip() if request.form['jaiotza'].strip() else None
         pasahitza = request.form['pasahitza'].strip() if request.form['pasahitza'].strip() else None
         pasahitza2 = request.form['pasahitza2'].strip() if request.form['pasahitza2'].strip() else None
         
         if pasahitza or pasahitza2:
            if pasahitza != pasahitza2:
               return render_template('editatu.html', home_endpoint=home_endpoint, 
                                    erabiltzailea=emaitza, error='Pasahitzak ez datoz bat')
            
            baliozko, mezua = self.eredu_kontroladorea.balioztatu_pasahitza(pasahitza, pasahitza2)
            if not baliozko:
               return render_template('editatu.html', home_endpoint=home_endpoint,
                                    erabiltzailea=emaitza, error=mezua)
         
         ondo, mezua = self.eredu_kontroladorea.eguneratu_erabiltzailea(
            erabiltzaile_izena, izena, email, jaiotze_data, pasahitza
         )
         
         if ondo:
            if izena and not user_id:
               session['user'] = izena
            if user_id:
               return redirect(url_for('kudeatu'))
            berria = izena if izena else erabiltzaile_izena
            emaitza_lista = self.eredu_kontroladorea.db.select(query, (berria,))
            emaitza = emaitza_lista[0] if emaitza_lista else None
            return render_template('editatu.html', home_endpoint=home_endpoint,
                                 erabiltzailea=emaitza, success=mezua)
         else:
            return render_template('editatu.html', home_endpoint=home_endpoint,
                                 erabiltzailea=emaitza, error=mezua)
      
      return render_template('editatu.html', home_endpoint=home_endpoint, erabiltzailea=emaitza)
   
   def erabiltzaileakKargatu(self):
      """Erabiltzaileak kudeatzeko orria (administratzaileak bakarrik)"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      if session.get('role', '').lower() != 'admin':
         flash('Ez duzu baimenik orri hau ikusteko', 'error')
         return redirect(url_for('menu'))
      
      erabiltzaileak_json = self.eredu_kontroladorea.erabiltzaileakKargatu()
      erabiltzaileak = json.loads(erabiltzaileak_json)
      
      current_user = session.get('user')
      erabiltzaileak = [user for user in erabiltzaileak if user.get('izena') != current_user]
      
      home_endpoint = 'menu_admin'
      
      return render_template('kudeatu.html', 
                           users=erabiltzaileak, 
                           home_endpoint=home_endpoint)
   
   def ezabatu(self, user_id):
      """Erabiltzaile bat ezabatu (administratzaileak bakarrik)"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      if session.get('role', '').lower() != 'admin':
         flash('Ez duzu baimenik', 'error')
         return redirect(url_for('menu'))
      
      query = "SELECT rola FROM Erabiltzailea WHERE izena = ?"
      emaitza = self.eredu_kontroladorea.db.select(query, (user_id,))
      
      if not emaitza:
         flash('Erabiltzailea ez da aurkitu', 'error')
         return redirect(url_for('kudeatu'))
      
      if session['user'] == user_id:
         flash('Ezin duzu zure burua ezabatu', 'error')
         return redirect(url_for('kudeatu'))
      
      ondo, mezua = self.eredu_kontroladorea.ezabatu(user_id)
      
      if ondo:
         flash(mezua, 'success')
      else:
         flash(mezua, 'error')
      
      return redirect(url_for('kudeatu'))
   
   def baimendu(self, user_id):
      """Erabiltzaile bat admin bihurtu (administratzaileak bakarrik)"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      if session.get('role', '').lower() != 'admin':
         flash('Ez duzu baimenik', 'error')
         return redirect(url_for('menu'))
      
      ondo, mezua = self.eredu_kontroladorea.baimendu(user_id, True)
      
      if ondo:
         flash(mezua, 'success')
      else:
         flash(mezua, 'error')
      
      return redirect(url_for('kudeatu'))
   
   def lagunakKargatu(self):
      """Jarraitzen dituen pertsonak ikusi"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      current_user = session.get('user')
      
      jarraitutakoak_json = self.eredu_kontroladorea.lagunakKargatu(current_user)
      jarraitutakoak = json.loads(jarraitutakoak_json)
      
      if session.get('role', '').lower() == 'admin':
         menu_endpoint = 'menu_admin'
      else:
         menu_endpoint = 'menu'
      
      return render_template('lagunak.html', 
                           lagunak=jarraitutakoak, 
                           menu_endpoint=menu_endpoint)
   
   def utzi_jarraitzen(self, jarraitua):
      """Erabiltzaile bat jarraitzen uztea"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      current_user = session.get('user')
      ondo, mezua = self.eredu_kontroladorea.utzi_jarraitzen(current_user, jarraitua)
      
      if ondo:
         flash(mezua, 'success')
      else:
         flash(mezua, 'error')
      
      return redirect(url_for('lagunak'))
   
   def gehituErabiltzailea(self, jarraitua=None):
      """Erabiltzaileak bilatu eta jarraitu"""
      if 'user' not in session:
         return redirect(url_for('login'))
      
      current_user = session.get('user')
      
      if jarraitua:
         ondo, mezua = self.eredu_kontroladorea.gehituErabiltzailea(current_user, jarraitua)
         
         if ondo:
            flash(mezua, 'success')
         else:
            flash(mezua, 'error')
         
         bilaketa = request.args.get('bilaketa', '')
         return redirect(url_for('gehituErabiltzailea', bilaketa=bilaketa))
      
      bilaketa = request.args.get('bilaketa', '')
      
      if session.get('role', '').lower() == 'admin':
         menu_endpoint = 'menu_admin'
      else:
         menu_endpoint = 'menu'
      
      erabiltzaileak = []
      if bilaketa:
         erabiltzaileak_json = self.eredu_kontroladorea.bilatu_erabiltzaileak(bilaketa, current_user)
         erabiltzaileak = json.loads(erabiltzaileak_json)
      
      return render_template('bilatzailea.html', 
                           erabiltzaileak=erabiltzaileak,
                           bilaketa=bilaketa,
                           menu_endpoint=menu_endpoint)
   
   def eguneratu_notifikazioak(self, jarraitua):
      if 'user' not in session:
         return redirect(url_for('login'))
      
      current_user = session.get('user')
      isilarazi = request.args.get('isilarazi', 'False').lower() == 'true'
      
      self.eredu_kontroladorea.eguneratu_notifikazioak(current_user, jarraitua, isilarazi)
      
      return redirect(url_for('lagunak'))
