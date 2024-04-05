const navigate = (url, token=undefined) => {
    // token = token || getToken();
    // console.log(token);
    // fetch(url, {
    //     method: "GET",
    //     headers: {
    //         "Authorization": `Bearer ${token}`
    //     }
    // })
    // .then(response => {
    //     if (response.ok) {
        //         window.location.href = url;
        //     } else {
            //         console.error("Failed to navigate:", response.statusText);
            //         // Handle error, e.g., show a message to the user
            //     }
            // })
            // .catch(error => {
                //     console.error("Fetch error:", error);
                //     // Handle error, e.g., show a message to the user
                // });
    window.location.href = url;
}

const navToTarget = (elem) => {
    const target = elem.getAttribute('target')
    navigate(target)
}

const setToken = (newToken) => {
    document.cookie = `access-token=${newToken}; path=/; max-age=3600;`;
}