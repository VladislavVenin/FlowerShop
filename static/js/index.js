document.addEventListener('DOMContentLoaded', function () {
    const quizButton = document.querySelector('.banner__btn')
    if(quizButton){
        quizButton.addEventListener('click', function () {
            window.location.href = "/quiz";
        })
    }

})