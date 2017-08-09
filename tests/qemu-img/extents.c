/* C Program to count the Number of Lines in a Text File  */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#define MAX_FILE_NAME 100

#define BDRV_SECTOR_BITS   9
#define BDRV_SECTOR_SIZE   (1ULL << BDRV_SECTOR_BITS)

typedef struct _linked_list {
   struct _linked_list *next;
   size_t offset;
   int length;
} extent_t;

bool does_sector_range_overlap_with_extent(extent_t **curr_ext, size_t *sector_begin, size_t *n)
{
    size_t qemu_offset = *sector_begin * BDRV_SECTOR_SIZE;
    size_t qemu_end = qemu_offset + *n * BDRV_SECTOR_SIZE - 1;
    size_t qemu_length = *n * BDRV_SECTOR_SIZE;
    extent_t *deref = *curr_ext;

    if (qemu_offset < deref->offset && qemu_end < deref->offset) {
        // qemu extent is completely before the current extent
        *sector_begin = deref->offset / BDRV_SECTOR_SIZE;
        return false;
    } else if (qemu_offset <= deref->offset  && qemu_end < deref->offset + deref->length) {
        // qemu extent has some overlap with current extent
        *sector_begin = deref->offset / BDRV_SECTOR_SIZE;
        *n = (qemu_offset + qemu_length - deref->offset )/BDRV_SECTOR_SIZE;
        return true;
    } else if (qemu_offset >= deref->offset && qemu_end < deref->offset + deref->length) {
        // qemu extent is entirely within extent
        return true;
    } else if (qemu_offset >= deref->offset + deref->length) {
        // qemu offset is outside of extent. Move the current extent
        *curr_ext = deref->next;
        if (*curr_ext) {
            *sector_begin = (*curr_ext)->offset / BDRV_SECTOR_SIZE;
        }
        *n = 0;
        return true;
    } else if (qemu_offset >= deref->offset &&
               qemu_offset < deref->offset + deref->length &&
               qemu_end > (deref->offset + deref->length)) {
        // qemu extent overlaps but extends beyond extent
        *n = (deref->offset + deref->length - qemu_offset) / BDRV_SECTOR_SIZE;
        *curr_ext = deref->next;
        return true;
    } else if (qemu_offset <= deref->offset  && qemu_offset + qemu_length >= deref->offset + deref->length) {
        // qemu extent is super set of extent
        *sector_begin = deref->offset / BDRV_SECTOR_SIZE;
        *n = deref->length / BDRV_SECTOR_SIZE;
        *curr_ext = deref->next;
        return true;
    }
    // we did not cover a case.
    assert(0);
}


int main()
{
    FILE *fp;
    int count = 0;  // Line counter (result)
    const char *filename = "extents";
    char col1[128], col2[128], col3[128];
    char c;  // To store a character read from file
    extent_t *extents = NULL, *last = NULL, *next = NULL, *start_extent = NULL;
    size_t total_sectors, range, start_sector, n, tb_to_backup;
 
    fp = fopen(filename, "r");

    // Check if file exists
    if (fp == NULL)
    {
        printf("Could not open file %s", filename);
        return 0;
    }
    //                                                        
    //
    fscanf(fp, "%s %s %s\n", col1, col2, col3);
    last = extents = calloc(1, sizeof(extent_t));
    while(!feof(fp)) {
       size_t offset, length;
       extent_t *ext = NULL;

       fscanf(fp, "%d %d %s\n", &offset, &length, col1);
       ext = calloc(1, sizeof(extent_t));
       ext->offset = offset;
       ext->length = length;
       ext->next = NULL;
       last->next = ext;
       last = ext;
    }
    //                                                                                     
    // Close the file
    fclose(fp);

    last = extents->next;
    tb_to_backup = 0;
    while (last) {
       printf("%d %d\n", last->offset, last->length);
       tb_to_backup += last->length;
       last = last->next;
    }
    printf("Total bytes to backup %d\n", tb_to_backup);
    printf("==============\n");

    total_sectors = 1024 * 1024 * 1024/512;
    range = 512;
    n = 512;
    start_sector = 0;
    start_extent = extents->next;
    tb_to_backup = 0;
    while (start_sector < total_sectors && start_extent) {
        while (!does_sector_range_overlap_with_extent(&start_extent, &start_sector, &n))
            ;
        printf("%d, %d\n", start_sector * 512, n * 512);
        start_sector += n;
        tb_to_backup += n * 512;
        n = range;
    }

    printf("Total bytes to backup %d\n", tb_to_backup);
    // free the list
    last = extents->next;
    while (last) {
       next = last->next;
       free(last);
       last = next;
    }
    free(extents);
    
    return 0;
}
