document.getElementById('addGoalBtn').onclick = function() {
    document.getElementById('goalModal').style.display = 'block';
};

document.getElementsByClassName('close')[0].onclick = function() {
    document.getElementById('goalModal').style.display = 'none';
};

// Schließen Sie das Modal, wenn der Benutzer außerhalb des Modals klickt
window.onclick = function(event) {
    const modal = document.getElementById('goalModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};