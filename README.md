# Flask MVC - Proba Practica Autobrand

O aplicație web în Python (Flask) bazată pe arhitectura MVC, complet containerizată cu Docker. Proiectul extinde structura open-source [flask-mvc](https://github.com/salimane/flask-mvc) cu funcționalități de extragere date din facturi PDF (e-Factura) în CSV și un task automatizat (cron) care rulează in fiecare ora in intervalul orar 12-18.

---

## 🛠️ Ghid de Pornire (Docker)

Tot mediul (Python, PostgreSQL, dependințe) este izolat în Docker. Nu este necesară instalarea lor locală.

### 📋 Prerechizite
- Instalează și pornește [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### 🚀 Pașii de pornire

#### 1. Deschide terminalul în folderul proiectului
Deschide o consolă (CMD / PowerShell / Terminal) și navighează în folderul în care se află fișierul `docker-compose.yml`.


#### 2.  Pornește containerele
Rulează următoarea comandă pentru a compila și lansa aplicația:
```bash
docker-compose up --build
```

#### 3.  Accesează aplicația
După ce procesul s-a finalizat, deschide browserul la adresea:

http://localhost:16000

#### 4.  Oprirea aplicației
Pentru a opri serverul, apasă Ctrl + C în terminalul în care rulează.

Pentru a șterge containerele din fundal (fără a pierde datele salvate în baza de date), rulează în același folder:
```bash
docker-compose down
```

## ⏱️ Verificare Loguri (Cronjob)

Sistemul execută automat un task de fundal in fiecare ora in intervalul **12-18*. Pentru a urmări logurile și activitatea acestuia în timp real, rulează în terminal:

```bash
docker exec -it flask-mvc-master-web-1 tail -f /var/log/cron_scraper.log
```

## 📝 TODO / Funcționalități Bonus (Abordare Teoretică și Practică)

Următoarele funcționalități reprezintă îmbunătățiri planificate pentru sistem, structurate conform cerințelor de bonus.
---

### 1. Preluare Curs Valutar și Salvare Preț dual (RON / Monedă Factură)
* **Obiectiv**: Interogarea cursului BNR din ziua curentă, salvarea acestuia și convertirea prețurilor produselor.
* **Abordare aleasă**: 
  Utilizarea unui client HTTP (`requests`) pentru a prelua fișierul XML zilnic oferit gratuit de BNR (sau un API de încredere precum `exchangerate-api`). Serviciul `scraping_service.py` va rula zilnic în fundal (prin cronjob) pentru a salva rata de schimb EUR/USD în baza de date locală.
---

### 2. Filtrare și Sortare în Interfața Web
* **Obiectiv**: Permiterea utilizatorului să caute rapid produse sau să le ordoneze după preț/cantitate în tabel.
* **Abordare aleasă**:
  Modificarea rutei de vizualizare pentru a accepta parametrii de query (ex: `/products?sort_by=price&order=desc&search=febi`). În loc de un simplu `.all()`, interogarea bazei de date se va face dinamic:
    ```python
    query = Product.query
    if search_keyword:
        query = query.filter(Product.denumire.ilike(f"%{search_keyword}%"))
    if sort_by == 'price':
        query = query.order_by(Product.pret_unitar.desc() if order == 'desc' else Product.pret_unitar.asc())
    ```
   Pe lânga asta este necesară adăugarea unui câmp de text de tip `Input` (căutare) și a unor săgeți de sortare pe capul de tabel în `index.html`, trimise către backend prin formulare simple sau link-uri dinamice.

---

### 3. Sistem Simplu de Autentificare (Auth)
* **Obiectiv**: Protejarea rutei de upload și a listei de produse împotriva accesului neautorizat.
* **Abordare aleasă**:
  - **Tehnologie**: Utilizarea extensiei standard **`Flask-Login`**.
  - **Structura Soluției**:
    - Crearea unui model nou `User` în baza de date (cu câmpurile `id`, `username`, `password_hash`).
    - Securizarea parolelor folosind algoritmul de hashing `werkzeug.security` (`generate_password_hash` și `check_password_hash`).
    - Crearea a două rute noi: `/login` și `/logout`.
  - **Protecția Rutelor**: Aplicarea decoratorului `@login_required` de la Flask-Login pe rutele sensibile (cum este `/upload-invoice`), redirecționând utilizatorii anonimi către pagina de autentificare.
