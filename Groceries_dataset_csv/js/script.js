// Full-Screen Image Modal Functionality
document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".chart-container img");
    const modal = document.createElement("div");
    modal.classList.add("image-modal");
    modal.innerHTML = '<span class="close">&times;</span><img>';
    document.body.appendChild(modal);

    const modalImg = modal.querySelector("img");
    const closeModal = modal.querySelector(".close");

    images.forEach(img => {
        img.addEventListener("click", function () {
            modal.style.display = "flex";
            modalImg.src = this.src;
        });
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    modal.addEventListener("click", function (e) {
        if (e.target !== modalImg) {
            modal.style.display = "none";
        }
    });
});
