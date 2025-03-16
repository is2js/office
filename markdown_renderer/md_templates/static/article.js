document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".article img").forEach(img => {
        const altText = img.getAttribute("alt");
        if (altText) {
            const captionText = altText.replace(/ -[^ ]+$/, ''); // " -xxxx" 제거

            // <figure> 생성
            const figure = document.createElement("figure");
            img.parentNode.insertBefore(figure, img); // 기존 위치에 figure 삽입
            figure.appendChild(img); // img를 figure 내부로 이동

            // <figcaption> 생성 후 추가
            const caption = document.createElement("figcaption");
            caption.textContent = captionText;
            figure.appendChild(caption);
        }
    });
});