// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        show_likers: false,
        add_mode: false,
        add_textarea: "",
        rows: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };
    app.complete = (rows) => {
        // Initializes useful fields of images.
        rows.map((row) => {
            row.thumb = null;
        })
    };
    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };
    app.add_post = function () {
        axios.post(add_post_url,
            {
                content: app.vue.add_textarea,
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                user_id: response.data.user_id,
                content: app.vue.add_textarea,
                full_name: response.data.full_name,
                //_state: {first_name: "clean", last_name: "clean"},
            });
            app.enumerate(app.vue.rows);
            //app.reset_form();
            app.set_add_status(false);
            });
        console.log("herhehrehh");
    };
    app.delete_post = function(row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_post_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
            });
    };
    app.add_thumb = function (row_idx, bool) {
        let id = app.vue.rows[row_idx].id;
            axios.post(add_thumb_url,
                {
                    post_id: id,
                    bool: bool, // row.first_name
                }).then(function (response) {
                app.vue.rows[row_idx].thumb = response.data.bool;
            });
    }
    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        set_add_status: app.set_add_status,
        add_post: app.add_post,
        delete_post: app.delete_post,
        add_thumb: app.add_thumb,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_posts_url)
            .then(function (response) {
                let rows = response.data.rows;
                app.enumerate(rows);
                app.complete(rows);
                app.vue.rows = rows;
            })
            .then(() => {
                for (let row of app.vue.rows) {
                    axios.get(get_thumb_url, { params: { "post_id": row.id } })
                        .then((result) => {
                            row.thumb = result.data.thumb;
                            console.log(result.thumb);
                        });
                }
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
