Wednesday, May 16, 2018

#include <string.h>
#include <stdio.h>
void RemoveDup(char *pcz_Str, char cz_Out[]);
int main()
{
    char cz_ShrtDesc[] = "     DISTRICT COLUMBIA REV    REV BDS BDS    REV 2007 A";
    char cz_Temp[40] ;
    memset(cz_Temp, 0, sizeof(cz_Temp));
    cz_ShrtDesc[strlen(cz_ShrtDesc)] = '\0';
    RemoveDup(cz_ShrtDesc, cz_Temp);
    printf("cz_Temp - %s", cz_Temp);
    return 0;
}


void RemoveDup(char *pcz_Str, char cz_Out[])
{
   char cz_Word[40] = {0};
   char cz_Pre[40] = {0};
   int i = 0;
   memset(cz_Pre, 0, sizeof(cz_Pre));
   memset(cz_Word, 0, sizeof(cz_Word));
   while(*pcz_Str)
   {

      while (*pcz_Str && *pcz_Str != ' ')
      {
         cz_Word[i++] = *pcz_Str;
         pcz_Str++;
      }
      cz_Word[i] = '\0';
      if(strlen(cz_Word) != 0)
      {
        printf("cz_Word= %s - %d\n", cz_Word, strlen(cz_Word));
        if(strcmp(cz_Pre, cz_Word) !=0){
         strncat(cz_Out, " ", 1);
         strcat(cz_Out, cz_Word);
         }
           
         strcpy(cz_Pre, cz_Word); 
         i = 0;
      }
      if(*pcz_Str)
         pcz_Str++;

   }
}
