//Podswietlanie przycisków z sensor i shape
function setSensor(m, el) {
    document.querySelectorAll('#group-sensor .btn').forEach(b => b.classList.remove('active-blue'));
    el.classList.add('active-blue');
}

function setShape(s, el) {
    document.querySelectorAll('#group-shape .btn').forEach(b => b.classList.remove('active-teal'));
    el.classList.add('active-teal');
}

//canvas
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');

//(0,0)
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;

//TODO: wyświetlanie punktów z 3D (x,y,z) na 2D (x,y) punkty mniejsze, większe



