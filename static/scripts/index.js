const navigate = (url, token=undefined) => {
    window.location.href = url;
}

const navToTarget = (elem) => {
    const target = elem.getAttribute('target')
    navigate(target)
}

const setToken = (newToken) => {
    document.cookie = `access-token=${newToken}; path=/; max-age=3600;`;
}

const colorClasses = {
    "black": "has-text-black",
    "blue": "has-text-link",
    "green": ["has-text-success", "is-light"]
}

const updateBodyTextColor = () => {
    let textColor = localStorage.getItem("my-walamoo-text-color")
    if (!textColor) 
        return;

    document.querySelectorAll("*").forEach((elem) => {
        for (const key in colorClasses) {
            if (elem.classList.contains(colorClasses[key])) {
                elem.classList.remove(colorClasses[key])
            }
        }
        if (textColor === "default") return
        elem.classList.add(colorClasses[textColor])
    })
}

const updateLanguage = () => {
    let language = localStorage.getItem("my-walamoo-language")
    if (!language || language !== "dfl") return;

    const toTranslate = document.querySelectorAll("p, h1, h2, h3, h4, h5, h6, button, td, th, label, #menu > .nav-link, .recordTitle, .recordValue")

    toTranslate.forEach(trans => {
        trans.textContent = translateToDFL(trans.textContent)
    })
}

const changeTextColor = (element) => {
    localStorage.setItem("my-walamoo-text-color", element.value);
    updateBodyTextColor()
}

const changeLanguage = (element) => {
    localStorage.setItem("my-walamoo-language", element.value);
    if (element.value !== "dfl") window.location.reload()
    updateLanguage()
}

updateBodyTextColor()
updateLanguage()

document.body.addEventListener('htmx:afterOnLoad', function() {
    setTimeout(() => {
        updateLanguage()
        updateBodyTextColor()
    }, 400)
});

const closePopup = (id) => {
    document.getElementById(id).remove()
}