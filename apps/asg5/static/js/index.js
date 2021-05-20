// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_id: 0,
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
        // Initializes useful fields of thumb.
        rows.map((row) => {
            row.thumb = null;
        })
    };
    app.map_likerhater = (rows) => {
        // Initializes useful fields of images.
        rows.map((row) => {
            row.show_likers = false,
            row.show_haters = false,
            row.likers = [];
            row.haters = [];
        })
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };
    app.set_show_likers = function (new_status, row_idx) {
        let id = app.vue.rows[row_idx].id;
        app.vue.rows[row_idx].show_likers = new_status;
        app.vue.rows[row_idx].show_haters = false;

        console.log(app.vue.rows[row_idx]);
        if (new_status === true) {
            axios.get(get_likerhater_url, { params: { "post_id": id, "bool": true } })
                .then(function (response) {
                    list = response.data.likerhater;
                    app.vue.rows[row_idx].likers = [];
                    for (let thum of list) {
                        app.vue.rows[row_idx].likers.push(thum['full_name'])
                    }
                    console.log(app.vue.rows[row_idx]);
                });  
        };
    };
    app.set_show_haters = function (new_status, row_idx) {
        let id = app.vue.rows[row_idx].id;
        app.vue.rows[row_idx].show_haters = new_status;
        app.vue.rows[row_idx].show_likers = false;
        if (new_status === true) {
            axios.get(get_likerhater_url, { params: { "post_id": id, "bool": false } })
                .then(function (response) {
                    list = response.data.likerhater;
                    app.vue.rows[row_idx].haters = [];
                    for (let thum of list) {
                        app.vue.rows[row_idx].haters.push(thum['full_name'])
                    }
                });
        };
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
                thumb: null,
                //_state: {first_name: "clean", last_name: "clean"},
            });
            app.enumerate(app.vue.rows);
            //app.reset_form();
            app.map_likerhater(app.vue.rows);
            app.set_add_status(false);
            });
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
                    bool: bool,
                }).then(function (response) {
                    app.vue.rows[row_idx].thumb = response.data.bool;
                    console.log(response.data.bool);
                    if (bool === true) {
                        app.vue.rows[row_idx].likers.push(response.data.full_name);   
                        }
                    if (bool === false) {
                        app.vue.rows[row_idx].haters.push(response.data.full_name);   
                    }
            });
    }
    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        set_add_status: app.set_add_status,
        set_show_likers: app.set_show_likers,
        set_show_haters: app.set_show_haters,
        map_likerhater: app.map_likerhater,
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
                app.map_likerhater(rows);
                app.vue.rows = rows;
            })
            .then(() => {
                for (let row of app.vue.rows) {
                    axios.get(get_thumb_url, { params: { "post_id": row.id } })
                        .then((result) => {
                            row.thumb = result.data.thumb;
                        });
                };
                axios.get(get_user_url)
                    .then(function (response) {
                    app.vue.user_id = response.data.user_id;
                });
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
