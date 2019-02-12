//------------------------------------------------------------------------------
// This file is part of MyDojo package (https://github.com/honzamach/mydojo).
//
// Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
// Use of this source is governed by the MIT license, see LICENSE file.
//------------------------------------------------------------------------------

module.exports = function(grunt) {

    // Minify given JSON file.
    function minify_json_file(src, tgt) {
        src_content = grunt.file.readJSON(src);
        tgt = tgt.replace(/\.json$/, '.min.json')
        grunt.file.write(
            tgt,
            JSON.stringify(src_content)
        );
        console.log("Minified JSON file '" + src + "' to '" + tgt + "'");
    }

    // Project configuration.
    grunt.initConfig({

        meta: grunt.file.readJSON('package.json'),

        // Project paths to important directories.
        paths_project: {
            'web_static':           'mydojo/static/',
            'web_templates':        'mydojo/templates/',
            'web_design_static':    'mydojo/blueprints/design/static/',
            'web_design_templates': 'mydojo/blueprints/design/templates/',
        },

        // ---------------------------------------------------------------------
        // Cleanup various locations.
        clean: {
            // Cleanup vendor directory.
            vendor: {
                src: [
                    "<%= paths_project.web_design_static %>vendor"
                ]
            }
        },

        // ---------------------------------------------------------------------
        // Running shell commands.
        shell: {
            // Make sure all third party libraries are installed.
            yarn_install: {
                command: 'yarn install'
            },
            // Compile language dictionaries.
            pybabel: {
                command: 'make pybabel-compile'
            },
        },

        // ---------------------------------------------------------------------
        // Copy certain files to appropriate locations.
        // ---------------------------------------------------------------------
        copy: {
            // Copy third-party components for web user interface.
            vendor: {
                files: [
                    // ----- Bootstrap
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/bootstrap/dist/css/',
                        src: './*',
                        dest: '<%= paths_project.web_design_static %>vendor/bootstrap/css/'
                    },
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/bootstrap/dist/js/',
                        src: './*',
                        dest: '<%= paths_project.web_design_static %>vendor/bootstrap/js/'
                    },
                    // ----- FontAwesome
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/@fortawesome/fontawesome-pro/css/',
                        src: './**',
                        dest: '<%= paths_project.web_design_static %>vendor/font-awesome/css/'
                    },
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/@fortawesome/fontawesome-pro/js/',
                        src: './**',
                        dest: '<%= paths_project.web_design_static %>vendor/font-awesome/js/'
                    },
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/@fortawesome/fontawesome-pro/webfonts/',
                        src: './**',
                        dest: '<%= paths_project.web_design_static %>vendor/font-awesome/webfonts/'
                    },
                    // ----- jQuery
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/jquery/dist/',
                        src: './**',
                        dest: '<%= paths_project.web_design_static %>vendor/jquery/js/'
                    },
                    // ----- Popper.js
                    {
                        expand: true,
                        flatten: true,
                        cwd: 'node_modules/popper.js/dist/',
                        src: './**',
                        dest: '<%= paths_project.web_design_static %>vendor/popper/js/'
                    },
                ]
            }
        },
    });

    // ---------------------------------------------------------------------
    // Load grunt modules.
    // ---------------------------------------------------------------------

    require('load-grunt-tasks')(grunt, { scope: 'devDependencies' });
    require('time-grunt')(grunt);

    // ---------------------------------------------------------------------
    // Setup custom tasks.
    // ---------------------------------------------------------------------

    grunt.registerTask(
        'webui',
       '(RUN) Build and install web user interface dependencies.',
       ['shell:yarn_install', 'shell:pybabel', 'clean:vendor', 'copy:vendor']
    );
    grunt.registerTask(
        'default',
       '(RUN) Alias for webui.',
       ['webui']
    );

};
