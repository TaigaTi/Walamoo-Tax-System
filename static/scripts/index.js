const navigate = (url) => {
    window.location.href = url
}

const navTarget = (elem) => {
    const target = elem.getAttribute('target')
    navigate(target)
}