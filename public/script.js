const flashCardButtonList  = document.querySelectorAll('.flash-card__action-button')

for (let flashCardButton of flashCardButtonList) {
    flashCardButton.addEventListener('click', () => {
        document.querySelector('main').classList.toggle('is-flipped');
    });
}