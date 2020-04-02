# Data Import

Place email text files here for them to be automatically imported.

The directory naming convention is `data/import/<class-type>/<class-label>`.

For the built-in `email` type with `business` and `personal` labels,
the import directory must include the type and the fully qualified domain label:

* `data/import/email/email.business`
* `data/import/email/email.personal`

For raw, un-annotated data, use the class domain's root label without specifying a subdomain:

* `data/import/email/email`

To re-use the same directories for multiple labels, use symlinks, e.g.:

```
$ cd email
$ ln -s email.business email.business.trips
$ ln -s email.personal email.personal.family
```
