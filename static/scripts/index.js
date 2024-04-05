const navigate = (url) => {
    window.location.href = url
}

const navToTarget = (elem) => {
    const target = elem.getAttribute('target')
    navigate(target)
}