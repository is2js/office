// document.addEventListener("DOMContentLoaded", function () {
//     document.querySelectorAll(".article img").forEach(img => {
//         const altText = img.getAttribute("alt");
//         if (altText) {
//             const captionText = altText.replace(/ -[^ ]+$/, ''); // " -xxxx" 제거
//
//             // <figure> 생성
//             const figure = document.createElement("figure");
//             img.parentNode.insertBefore(figure, img); // 기존 위치에 figure 삽입
//             figure.appendChild(img); // img를 figure 내부로 이동
//
//             // <figcaption> 생성 후 추가
//             const caption = document.createElement("figcaption");
//             caption.textContent = captionText;
//             figure.appendChild(caption);
//         }
//     });
// });

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".article img").forEach((img, index, imgArray) => {
        const altText = img.getAttribute("alt");
        // altText가 존재하고, " -" 뒤에 공백 없는 문자열이 오는 패턴 검사
        if (altText && / -[^ ]+$/.test(altText)) { // " -" 뒤에 공백 없는 문자열이 오는 패턴 검사
            const captionText = altText.replace(/ -[^ ]+$/, ''); // 마지막 " -xxxx..." 제거

            // <figure> 생성
            const figure = document.createElement("figure");
            img.parentNode.insertBefore(figure, img); // 기존 위치에 figure 삽입
            figure.appendChild(img); // img를 figure 내부로 이동

            // <figcaption> 생성 후 추가
            const caption = document.createElement("figcaption");
            caption.textContent = captionText;
            figure.appendChild(caption);
        } else {
            // 현재 이미지의 부모에서, 위쪽에서 이미 생성된 wrapper 목록을 가져와서, 가장 마지막 wrapper를 찾는다.
            let parent = img.parentNode;
            let wrappers = parent.querySelectorAll(".img-wrapper"); // ✅ 기존 wrapper 목록 가져오기
            let lastWrapper = wrappers[wrappers.length - 1]; // ✅ 가장 마지막 wrapper 찾기

            let currentWidth = 0;

            // ✅ 마지막 wrapper속 이미지들  width 합을 currentWidth에 저장
            if (lastWrapper) {
                let existingImgs = [...lastWrapper.querySelectorAll("img")];
                currentWidth = existingImgs.reduce((sum, img) => {
                    let width = img.getAttribute("width") || window.getComputedStyle(img).width;
                    return sum + (parseFloat(width) || 100);
                }, 0);
            }

            // 현재 이미지 width를 계산해서후, 마지막 wrapper의 width총합(currentWidth)과 한다.
            let imgWidth = img.getAttribute("width") || window.getComputedStyle(img).width;
            imgWidth = parseFloat(imgWidth) || 100;

            let newTotalWidth = currentWidth + imgWidth;

            // console.log(`현재 이미지(${index}): ${img.getAttribute("alt")}`);
            // console.log(`현재 wrapper 총 너비: ${currentWidth}`);
            // console.log(`현재 이미지 너비: ${imgWidth}`);
            // console.log(`새로운 총 너비: ${newTotalWidth}`);

            let isInsideTable = false;
            // ✅ 마지막 wrapper가 없거나, totalWidth의 너비가 100%를 초과하면 새로운 wrapper 생성
            if (!lastWrapper || newTotalWidth > 100) {
                lastWrapper = document.createElement("div");
                lastWrapper.classList.add("img-wrapper");
                lastWrapper.style.display = "flex";
                lastWrapper.style.justifyContent = "space-around";
                lastWrapper.style.alignItems = "center";
                lastWrapper.style.flexWrap = "wrap";
                lastWrapper.style.margin = "0.5em auto";

                // lastWrapper.style.width = "100%";
                // wrapper가 table속에 있다면 100% 말고, auto로
                // ✅ 테이블 내부인지 확인하고 width 조정
                let tempParent = parent;
                while (tempParent) {
                    if (tempParent.tagName === "TABLE") {
                        isInsideTable = true;
                        break;
                    }
                    tempParent = tempParent.parentElement;
                }

                if (isInsideTable) {
                    lastWrapper.style.width = "auto"; // ✅ 테이블 내부라면 auto
                } else {
                    lastWrapper.style.width = "100%"; // ✅ 일반적인 경우 100%
                }

                parent.appendChild(lastWrapper); // ✅ 새 wrapper를 부모에 추가
                currentWidth = 0; // ✅ 새 그룹이므로 다시 계산 시작
            }

            lastWrapper.appendChild(img);
            // currentWidth += imgWidth; // ✅ 새 wrapper에서 너비 계산 시작

            // ✅ 이미지 스타일 설정

            // img.style.maxWidth = "fit-content";
            img.style.maxWidth = "100%";
            img.style.borderRadius = "1em";
            img.style.border = "1px solid #f1f3f6";

            if (!img.hasAttribute("height")) {
                img.style.height = "auto"; // 비율 유지
            }

            if (!img.hasAttribute("width")) {
                // img.style.width = "100%"; // 이미지 너비 100% 설정

                // width도 없고, table 속에 있다면, 180px을 기본으로 설정
                if (isInsideTable) {
                    // img.style.width = "180px";
                    // ✅ 테이블 내부인지 다시 확인 (table > tr > td 구조)
                    let tdParent = img.closest("td"); // 가장 가까운 <td> 찾기
                    if (tdParent) {
                        tdParent.style.maxWidth = "180px";
                        tdParent.style.padding = "0";

                        lastWrapper.style.margin = "0";


                        img.style.width = "100%";        // <td>에 꽉 차도록 설정
                        img.style.height = "100%";       // 높이도 채우도록 설정
                        img.style.objectFit = "cover";   // 비율 유지하면서 <td> 가득 채우기
                        img.style.maxWidth = "none";     // 최대 너비 제한 해제

                        img.style.borderRadius = "0";
                        img.style.border = "none";

                    }
                } else {
                    img.style.width = "100%"; // 이미지 너비 100% 설정
                }
            }
        }
    });
});