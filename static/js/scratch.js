const Scratch = {
    FlashApp: {
        ASobj: document.getElementById("scratch"),
        API: {
            swf: null,
            attach(el) { this.swf = el; Scratch.FlashApp.ASobj = el; },
            call(name, ...args) {
                if (this.swf && typeof this.swf[name] === 'function') {
                    try { return this.swf[name](...args); }
                    catch (e) { console.error('AS call failed', name, e); }
                }
            },
            setEditorMode(b) { this.call('ASsetEditMode', !!b); },
            setLoginUser(u) { this.call('ASsetLoginUser', String(u)); },
            setScratcher(b) { this.call('ASsetScratcher', !!b); },
            setNewProject(id, title) { this.call('ASsetNewProject', id, title); },
            remixProject() { this.call("ASremixProject") },
            shareProject(b) { this.call("ASsetShared", !!b) },
            downloadProject() { this.call("ASdownload") },
            loadProject(owner, id, title, shared, autostart) { this.call("ASloadProject", owner, id, title, shared, autostart) },
            setPresentationMode(b) { this.call("ASsetPresentationMode", !!b) },
            isEditor() { return this.call("ASisEditMode") },
            setEmbedMode(b) { this.call("ASsetEmbedMode", !!b) },
            createNewProject() { this.call("AScreateProject", Scratch.user.name, null) },
            AprilFools() { this.call("April's Idiots") },
        },
        isRemix: false,
    },
    user: {
        name: "",
        id: NaN
    },
    auth: {
        logout: async function () {
            await fetch(`${window.location.origin}/site-api/auth/logout/`, { method: "POST" });
            Scratch.FlashApp.API.setLoginUser("");
            try {
                projectId;
            } catch {
            window.location.href = window.location.pathname;
            }
        },
        login: async function () {
            const username = prompt("Username:", "");
            const password = prompt("Password:", "");
            if (!username || !password) return;

            const res = await fetch(`${window.location.origin}/site-api/auth/login/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (data.ok) {
                // Tell SWF who is logged in
                Scratch.FlashApp.API.setLoginUser(data.username);
                if (projectOwner != data.username && !projectId) {
                    Scratch.FlashApp.API.call("ASexportProject");
                }
            } else {
                alert("Login failed");
            }
        }
    }
};