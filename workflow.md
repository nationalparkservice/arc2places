Workflows:
==========

The following workflows are probable.  I do not know what workflow any unit will use.
I doubt all units will want the same workflow. There may be workflows I have not imagined.
I am providing tools to support workflow #3, with the goal of also supporting workflow #6.
Details on the tools can be found [here](https://github.com/nationalparkservice/arc2places/blob/master/Tools.md)

1) Places Master
----------------
* Unit[^1] sends ArcGIS data to NPMap team.
* NPMap imports data into Places.
* ArcGIS data is discarded or set to read only.
* All updates for Unit data occur in Places editor.
* If Unit data is needed in ArcGIS format it is extracted from Places.

2) GIS Master 1
---------------
* Unit sends ArcGIS data to NPMap team.
* NPMap imports data into Places.
* Unit edits/maintains ArcGIS data.
* Unit does not edit data in Places editor - edits in Places to features in Unit are ignored by Unit[^2].
* Unit periodically sends ArcGIS refresh to NPMap team.  NPMap purges and replaces Unit data in Places.
* Any edits made in Places are lost.

3) GIS Master 2
---------------
* Unit uploads ArcGIS data to Places
* Unit saves the upload log, and enables ArcGIS editor tracking for change detection.
* Unit does not edit data in Places editor - edits in Places to features in Unit are ignored by Unit[^2].
* Unit edits/maintains ArcGIS data.
* Unit periodically uses upload log and editor tracking to calculate ArcGIS changes and pushes them to Places

4) Dual Master 1a
-----------------
* Process starts with workflow #1 or #2, but edits occur independently in both ArcGIS and Places.
* Unit periodically compares data in Places and ArcGIS and manually reconciles the two systems by adding/updating/deleting from the two systems to get them back into sync.

5) Dual Master 1b
-----------------
* Process starts with workflow #1 or #2, but edits occur independently in both ArcGIS and Places.
* Unit periodically sends ArcGIS data to NPMap team.
* NPMap team manually or with tools yet to be developed updates Places with ArcGIS data.[^3]
* Unit periodically reviews Places for changes and manually or with tools yet to be developed updates ArcGIS data.

6) Dual Master 2
----------------
* Process starts with workflow #3, but edits occur independently in both ArcGIS and Places.
* Unit periodically pulls changes in Places data and manually or with tools yet to be developed updates ArcGIS data.
* Unit uses process in workflow #3 to push ArcGIS changes to Places

7) Dual Master 3
----------------
* Process starts with Workflow #1, 2, or 3, but edits occur independently in both ArcGIS and Places.
* ArcGIS and Places diverge.
* They are maintained independently and are never reconciled.[^4]

[^1]: A unit is a park, region or some other organization responsible for *unit data* within the *unit area*

[^2]: NPMap team may not ignore these edits, and they may appear in public NPMap products like Park Tiles or CartoDB

[^3]: NPMap team would need to agree to this additional workload.

[^4]: While this is duplicative, it may not be bad as the two systems have different needs and purposes.

