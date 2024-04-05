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
    "default": "has-text-light",
    "black": "has-text-black",
    "blue": "has-text-link",
    "green": ["has-text-success", "is-light"]
}

const updateBodyTextColor = () => {
    let textColor = localStorage.getItem("my-walamoo-text-color") || "black"
    document.querySelectorAll("*").forEach((elem) => {
        for (const key in colorClasses) {
            if (elem.classList.contains(colorClasses[key])) {
                elem.classList.remove(colorClasses[key])
            }
        }
        // if (textColor === "default") return
        elem.classList.add(colorClasses[textColor])
    })
}

const changeTextColor = (element) => {
    localStorage.setItem("my-walamoo-text-color", element.value);
    updateBodyTextColor()
}

updateBodyTextColor()